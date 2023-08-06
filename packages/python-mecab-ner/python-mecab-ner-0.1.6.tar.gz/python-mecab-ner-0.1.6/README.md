# mecab_ner

## Table of Contents
  * [Installation](#installation)
  * [Quick start](#quick-start)
  * [Features](#features)
  
## Installation

Download using pip via pypi.

```bash
$ pip install 'python-mecab-ner' --upgrade
```
(Mac/homebrew users may need to use ``pip3``)


## A Simple Example
```python
from python_mecab_ner.mecab_ner import MecabNer

mecab_ner = MecabNer()
test_sentence = "아이묭 노래 들으면서 신촌 제철 딸기랑 거봉 감이 먹고 싶어"
print(mecab_ner.parse(test_sentence))
print(mecab_ner.morphs(test_sentence))
['아이묭', '노래', '들으면서', '들으면서', '신촌 제철 딸기', '랑', '거봉 감', '이', '먹', '고', '싶', '어']

mecab_ner.ners(test_sentence)
# [('아이묭', 'music_singer', '가수'), ('신촌 제철 딸기', 'fruit', '과일'), ('거봉 감', 'fruit', '과일')]
```

##


## Features
  * Python library to get NER using Mecab