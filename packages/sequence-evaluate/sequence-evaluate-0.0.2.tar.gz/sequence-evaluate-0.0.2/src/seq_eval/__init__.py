import numpy as np
from collections import Counter
from rouge import Rouge
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import SmoothingFunction
from sentence_transformers import SentenceTransformer, util