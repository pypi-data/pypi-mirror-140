# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# Copyright (c) 2021 scart97

from string import ascii_lowercase

import pytest

import torch
from hypothesis import given
from hypothesis.strategies import text

from thunder.text_processing.tokenizer import char_tokenizer
from thunder.text_processing.vocab import Vocabulary


@pytest.fixture
def complex_vocab(request):
    vocab = Vocabulary(
        tokens=[" "] + list(ascii_lowercase),
        pad_token="<pad>",
        unknown_token="<unk>",
        start_token="<bos>",
        end_token="<eos>",
    )
    return vocab


@pytest.fixture
def simple_vocab(request):
    vocab = Vocabulary(tokens=[" "] + list(ascii_lowercase))
    return vocab


def test_vocab_mapping_is_bidirectionally_correct(complex_vocab: Vocabulary):
    assert len(complex_vocab.itos) == len(complex_vocab.stoi)
    for k, v in complex_vocab.stoi.items():
        assert complex_vocab.itos[v] == k


def test_nemo_vocab_mapping_is_bidirectionally_correct(simple_vocab: Vocabulary):
    assert len(simple_vocab.itos) == len(simple_vocab.stoi)
    for k, v in simple_vocab.stoi.items():
        assert simple_vocab.itos[v] == k


def test_vocab_blank_is_not_the_unknown(complex_vocab: Vocabulary):
    unknown_idx = complex_vocab.itos.index(complex_vocab.unknown_token)
    assert complex_vocab.blank_idx != unknown_idx
    assert complex_vocab.blank_token != complex_vocab.unknown_token


def test_numericalize_adds_unknown_token(complex_vocab: Vocabulary):
    out = complex_vocab.numericalize(["a", "b", "c", "$"])
    unknown_idx = complex_vocab.itos.index(complex_vocab.unknown_token)
    expected = torch.Tensor([1, 2, 3, unknown_idx])
    assert (out == expected).all()


def test_numericalize_nemo_ignores_unknown(simple_vocab: Vocabulary):
    out = simple_vocab.numericalize(["a", "b", "c", "$"])
    expected = torch.Tensor([1, 2, 3])
    assert (out == expected).all()


def test_numericalize_decode_is_bidirectionally_correct(complex_vocab: Vocabulary):
    inp = ["a", "b", "c", "d", "e"]
    out1 = complex_vocab.numericalize(inp)
    out = complex_vocab.decode_into_text(out1)
    assert out == inp


def test_nemo_numericalize_decode_is_bidirectionally_correct(simple_vocab: Vocabulary):
    inp = ["a", "b", "c", "d", "e"]
    out1 = simple_vocab.numericalize(inp)
    out = simple_vocab.decode_into_text(out1)
    assert out == inp


def test_add_special_tokens(complex_vocab: Vocabulary):
    inp = ["a", "b", "c"]
    out = complex_vocab.add_special_tokens(inp)
    assert out == [complex_vocab.start_token, "a", "b", "c", complex_vocab.end_token]


def test_nemo_doesnt_add_special_tokens(simple_vocab: Vocabulary):
    inp = ["a", "b", "c"]
    out = simple_vocab.add_special_tokens(inp)
    assert out == ["a", "b", "c"]


def test_special_idx_are_different(complex_vocab: Vocabulary):
    all_tokens = set(
        [
            complex_vocab.start_token,
            complex_vocab.end_token,
            complex_vocab.pad_token,
            complex_vocab.unknown_token,
            complex_vocab.blank_token,
        ]
    )
    # There's no problem if the blank_idx == pad_idx
    assert len(all_tokens) >= 4


@given(text(min_size=1, max_size=100))
def test_nemo_compat_mode(sample):
    vocab = Vocabulary(tokens=["a", "b", "c"])
    assert len(vocab.itos) == 4
    assert vocab.blank_idx == 3

    out = vocab.numericalize(char_tokenizer(sample))
    if out.numel() > 0:
        assert out.max() < 4
        assert out.min() >= 0
