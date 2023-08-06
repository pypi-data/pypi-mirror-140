from typing import List, Generator

from mecab_generator import MecabGenerator
from mecab_parser import MeCabParser
from mecab_storage import MeCabStorage
from domain.entity import MecabCategory
from utility.mecab_helper import contain_pattern_list
import copy


def infer_backward(mecab_parsed_list: List, mecab_category_item: MecabCategory) -> MecabCategory:
    """ pos에 따라 end_index 변경"""

    for idx_range in range(mecab_category_item.end_idx, len(mecab_parsed_list) - 1, 1):
        if mecab_parsed_list[idx_range][MeCabNer.MECAB_FEATURE_IDX].pos in ["NNG", "NNP"]:
            mecab_category_item.end_idx = mecab_parsed_list[idx_range][1].mecab_token_idx + 1
            continue
        elif mecab_parsed_list[idx_range][MeCabNer.MECAB_FEATURE_IDX].pos in ["MM"]:
            mecab_category_item.end_idx = mecab_parsed_list[idx_range][1].mecab_token_idx + 1
            continue
        break
    return mecab_category_item


def infer_entity(mecab_parsed_list: List, mecab_category_item: MecabCategory) -> MecabCategory:
    """ pos에 따라 start_index 변경"""

    end_point = 0
    if mecab_category_item.start_idx == 1:
        end_point = -1

    for idx_range in range(mecab_category_item.start_idx - 1, end_point, -1):
        if mecab_parsed_list[idx_range][MeCabNer.MECAB_FEATURE_IDX].pos in ["NNG", "NNP"]:
            mecab_category_item.start_idx = mecab_parsed_list[idx_range][1].mecab_token_idx
            continue
        break
    return mecab_category_item

def integrate_many_entity_index(mecab_entity_category_list: List, length: int) -> List:
    """인덱스 값에 엔티티가 있는 경우, 없는 경우 구분"""
    blank = [MeCabNer.EMPTY_WORD] * length
    for mecab_entity_category_item in mecab_entity_category_list:
        for i in range(mecab_entity_category_item.start_idx, mecab_entity_category_item.end_idx, 1):
            blank[i] = MeCabNer.FULL_WORD
    return blank

def gen_integrated_entity(blank_list: List) -> Generator:

    """
    엔티티가 포함된 인덱스는 1로 색칠되어 있다. 없는 인덱스 반환
    """

    start_idx = None
    end_idx = None
    switch_on = True
    for idx, item in enumerate(blank_list):
        if item == MeCabNer.FULL_WORD:
            end_idx = idx # 한번은 0이 된다.

            if switch_on: # 스위치 켜지면 start_index를 시작점으로 잡는다.
                start_idx = idx

            switch_on = False

            if idx != len(blank_list) - 1: # 인덱스가 끝이 아니라면, 다음 단어를 탐색한다.
                continue

        if (switch_on is False) and (end_idx is not None):
            yield start_idx, end_idx
            start_idx = None
            end_idx = None
            switch_on = True

class MeCabNer:
    """
    엔티티 추출하는 클래스
    - 앞에 단어 품사를 통한 추론 기능
    - 뒤에 단어 품사를 통한 추론 기능
    """

    MIN_MEANING = 2
    START_IDX = 0
    END_IDX = 1
    ONE_WORD = 1
    MECAB_FEATURE_IDX = 1
    WORD_IDX = 0
    ENTITY = 0
    INFER_FORWARD = 1
    INFER_BACKWARD = 2
    EMPTY_WORD = 0
    FULL_WORD = 1

    def __init__(self, storage_mecab_path: str):

        self.gen_all_mecab_category_data = MecabGenerator.gen_all_mecab_category_data \
            (storage_path=storage_mecab_path, need_parser=False)

    def get_category_entity(self, sentence: str) -> Generator:
        """ mecab 저장 데이터와 storage 데이터의 길이가 같은지 확인 """
        mecab_parsed_list = list(MeCabParser(sentence=sentence).gen_mecab_compound_token_feature())

        for mecab_category_item in self.gen_all_mecab_category_data:
            mecab_parsed_copied = copy.deepcopy(mecab_parsed_list)
            large_category, medium_category, mecab_token_data = mecab_category_item

            for small_category in mecab_token_data.keys():

                for small_category_item in mecab_token_data[small_category]:

                    original_data, mecab_data = small_category_item.split(MecabGenerator.ITEM_BOUNDARY)

                    contain_pattern = contain_pattern_list(mecab_data, mecab_parsed_copied)

                    if contain_pattern:
                        for pattern_item in contain_pattern:
                            self.prevent_compound_token(pattern_item, mecab_parsed_copied)
                            yield MecabCategory(large_category=large_category, medium_category=medium_category,
                                                small_category=small_category,
                                                start_idx=pattern_item[self.START_IDX],
                                                end_idx=pattern_item[self.END_IDX])
                        continue

                    space_token_contain_pattern = contain_pattern_list(original_data, mecab_parsed_copied)

                    if (len(original_data) >= self.MIN_MEANING) and space_token_contain_pattern:
                        for pattern_item in contain_pattern:
                            self.prevent_compound_token(pattern_item, mecab_parsed_copied)
                            yield MecabCategory(large_category=large_category, medium_category=medium_category,
                                                small_category=small_category,
                                                start_idx=pattern_item[self.START_IDX],
                                                end_idx=pattern_item[self.END_IDX])

    def prevent_compound_token(self, pattern_item: List, mc_ps: List) -> None:
        for pattern_idx_item in range(pattern_item[self.START_IDX], pattern_item[self.END_IDX], self.ONE_WORD):
            mc_ps[pattern_idx_item] = ("*", mc_ps[pattern_idx_item][self.MECAB_FEATURE_IDX])

    def get_entities(self, sentence: str, status=0):
        mecab_parsed_list = list(MeCabParser(sentence=sentence).gen_mecab_compound_token_feature())
        for category_item in self.get_category_entity(sentence=sentence):
            if status == self.INFER_FORWARD:
                category_item = infer_entity(mecab_parsed_list, category_item)
            elif status == self.INFER_BACKWARD:
                category_item = infer_backward(mecab_parsed_list, category_item)
            entity_list = list(self.get_entity(mecab_parsed_list, category_item.start_idx, category_item.end_idx))
            entity_str = " ".join(entity_list)
            yield MecabCategory(large_category=category_item.large_category,
                                medium_category=category_item.medium_category,
                                small_category=category_item.small_category,
                                start_idx=category_item.start_idx,
                                end_idx=category_item.end_idx,
                                entity=entity_str)

    def get_entity(self, mecab_parsed_list: List, start_idx: int, end_idx: int) -> str:

        """ start_index와 end_index를 바탕으로 리스트에서 해당 값 추출 """

        for step_idx in range(start_idx, end_idx, self.ONE_WORD):
            yield mecab_parsed_list[step_idx][self.WORD_IDX]

    def gen_integrated_entities(self, sentence, status):
        mecab_parsed_list = list(MeCabParser(sentence=sentence).gen_mecab_compound_token_feature())
        mecab_entity_category_list = list(self.get_entities(sentence, status=status))

        many_entity_index_list = integrate_many_entity_index(mecab_entity_category_list, length=len(mecab_parsed_list))

        for integrated_entity_item in gen_integrated_entity(many_entity_index_list):
            end_idx = integrated_entity_item[1] + 1
            start_idx = integrated_entity_item[0]
            mecab_parsed_token = mecab_parsed_list[start_idx:end_idx]
            restore_tokens = MeCabStorage().reverse_compound_tokens(mecab_parsed_token)
            restore_sentence = " ".join(restore_tokens)
            for entity_category_item in mecab_entity_category_list:
                if entity_category_item.end_idx == end_idx:
                    small_category_replace = entity_category_item.small_category.replace("#", "").strip()
                    yield MecabCategory(large_category=entity_category_item.large_category,
                                        medium_category=entity_category_item.medium_category,
                                        small_category=small_category_replace,
                                        start_idx=entity_category_item.start_idx,
                                        end_idx=entity_category_item.end_idx,
                                        entity=restore_sentence)