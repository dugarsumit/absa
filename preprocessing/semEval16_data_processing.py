import os
import sys

sys.path.append(os.getcwd())
from config.settings import WORD_FREQ_FILE, VOCAB_TO_CODE_FILE, CODE_TO_VOCAB_FILE, CODE_TO_EMBED_FILE
import numpy as np
from utils.data_util import read_binary, write_binary
from utils.util import load_glove_embeddings, load_fastText_embeddings, load_oov_fastText_embeddings
import spacy
from collections import defaultdict
import random

# ---SCRIPT DEPENDENCIES----
# python -m spacy download en
# --------------------------

# -----CHANGE THESE VALUES ACCORDINGLY BEFORE RUNNING THE SCRIPT-----
TYPE = 'train'
# TYPE = 'test'
# TYPE = 'val'
FILE_NAME = 'restaurant'
# FILE_NAME = 'laptops'
EMBEDDING_TYPE = 'fasttext'
# EMBEDDING_TYPE = 'glove'
# EMBEDDING_TYPE = None
# -------------------------------------------------------------------
FORMATTED_FILE_NAME = 'formatted_' + FILE_NAME + '_' + TYPE + '.pickle'
PROCESSED_FILE_NAME = 'processed_' + TYPE + '.pickle'

EMBEDDING_DIMENSION = 300
MAX_VOCAB_SIZE = 50001
UNKNOWN_EMBEDDING = np.random.randn(EMBEDDING_DIMENSION)
PAD = 0
PAD_EMBEDDING = np.zeros(EMBEDDING_DIMENSION)
NLP = spacy.load('en_core_web_sm')

HOTELS_ASPECT_WORDS = ['hotel', 'general', 'prices', 'design', 'features', 'cleanliness', 'comfort',
                       'quality', 'style', 'options', 'miscellaneous', 'rooms', 'room', 'amenities', 'facilities',
                       'service', 'location', 'food', 'drinks', 'Hotel', 'General', 'Prices', 'Design', 'Features',
                       'Cleanliness', 'Comfort', 'Quality', 'Style', 'Options', 'Miscellaneous', 'Rooms', 'Room',
                       'Amenities', 'Facilities', 'Service', 'Location', 'Food', 'Drinks']

HOTELS_ALL_POSSIBLE_ASPECTS = [['hotel', 'general'], ['hotel', 'prices'], ['hotel', 'design', 'features'],
                               ['hotel', 'cleaniness'], ['hotel', 'comfort'], ['hotel', 'quality'],
                               ['hotel', 'miscellaneous'],
                               ['rooms', 'general'], ['rooms', 'prices'], ['rooms', 'design', 'features'],
                               ['rooms', 'cleaniness'], ['rooms', 'comfort'], ['rooms', 'quality'],
                               ['rooms', 'miscellaneous'],
                               ['room', 'amenities', 'general'], ['room', 'amenities', 'prices'],
                               ['room', 'amenities', 'design', 'features'],
                               ['room', 'amenities', 'cleaniness'], ['room', 'amenities', 'comfort'],
                               ['room', 'amenities', 'quality'],
                               ['room', 'amenities', 'miscellaneous'], ['service', 'general'], ['location', 'general'],
                               ['food', 'drinks', 'prices'], ['food', 'drinks', 'quality'],
                               ['food', 'drinks', 'style', 'options']]

RESTAURANT_ASPECT_WORDS = ['restaurant', 'general', 'prices', 'miscellaneous', 'food', 'quality', 'style', 'options',
                           'drinks', 'ambience', 'service', 'location', 'Restaurant', 'General', 'Prices',
                           'Miscellaneous',
                           'Food',
                           'Quality', 'Style', 'Options', 'Drinks', 'Ambience', 'Service', 'Location']

RESTAURANT_ALL_POSSIBLE_ASPECTS = [['restaurant', 'general'], ['restaurant', 'prices'], ['restaurant', 'miscellaneous'],
                                   ['food', 'prices'], ['food', 'quality'], ['food', 'style', 'options'],
                                   ['drinks', 'prices'], ['drinks', 'quality'], ['drinks', 'style', 'options'],
                                   ['ambience', 'general'],
                                   ['service', 'general'],
                                   ['location', 'general']]

RESTAURANT_ASPECT_WORD_INDEX_MAP = {
    'foodstyleoptions': 0,
    'foodquality': 1,
    'drinksprices': 2,
    'foodprices': 3,
    'ambiencegeneral': 4,
    'drinksstyleoptions': 5,
    'locationgeneral': 6,
    'drinksquality': 7,
    'restaurantprices': 8,
    'restaurantmiscellaneous': 9,
    'servicegeneral': 10,
    'restaurantgeneral': 11,
    'none': 12
}

RESTAURANT_INDEX_TO_ASPECT_WORD_MAP = {
    0: 'foodstyleoptions',
    1: 'foodquality',
    2: 'drinksprices',
    3: 'foodprices',
    4: 'ambiencegeneral',
    5: 'drinksstyleoptions',
    6: 'locationgeneral',
    7: 'drinksquality',
    8: 'restaurantprices',
    9: 'restaurantmiscellaneous',
    10: 'servicegeneral',
    11: 'restaurantgeneral',
    12: 'none'
}

LAPTOPS_ASPECT_WORDS = ['laptop', 'display', 'cpu', 'motherboard', 'hard', 'disc', 'memory', 'battery', 'power',
                        'supply', 'keyboard', 'mouse', 'fan', 'fans', 'cooling', 'optical', 'drives', 'drive', 'ports',
                        'graphics', 'multimedia', 'devices', 'device', 'hardware', 'os', 'software', 'warranty',
                        'shipping', 'support', 'company', 'general', 'price', 'quality', 'operation', 'performance',
                        'usability', 'design', 'features', 'portability', 'connectivity', 'miscellaneous',
                        'Laptop', 'Display', 'CPU', 'Cpu', 'Motherboard', 'Hard', 'Disc', 'Memory', 'Battery', 'Power',
                        'Supply', 'Keyboard', 'Mouse', 'Fan', 'Fans', 'Cooling', 'Optical', 'Drives', 'Drive', 'Ports',
                        'Graphics', 'Multimedia', 'Devices', 'Device', 'Hardware', 'OS', 'Os', 'Software', 'Warranty',
                        'Shipping', 'Support', 'Company', 'General', 'Price', 'Quality', 'Operation', 'Performance',
                        'Usability', 'Design', 'Features', 'Portability', 'Connectivity', 'Miscellaneous'
                        ]

LAPTOPS_ALL_POSSIBLE_ASPECTS = [['laptop', 'general'], ['laptop', 'operation', 'performance'], ['laptop', 'usability'],
                                ['laptop', 'portability'], ['laptop', 'price'], ['laptop', 'quality'],
                                ['laptop', 'design', 'features'], ['laptop', 'miscellaneous'],
                                ['laptop', 'connectivity'],
                                ['display', 'usability'], ['display', 'design', 'features'], ['display', 'quality'],
                                ['display', 'general'], ['display', 'operation', 'performance'],
                                ['cpu', 'operation', 'performance'], ['cpu', 'quality'], ['cpu', 'miscellaneous'],
                                ['cpu', 'design', 'features'],
                                ['motherboard', 'quality'],
                                ['hard', 'disc', 'design', 'features'], ['hard', 'disc', 'quality'],
                                ['memory', 'design', 'features'],
                                ['battery', 'quality'], ['battery', 'miscellaneous'],
                                ['battery', 'operation', 'performance'],
                                ['power', 'supply', 'quality'], ['power', 'supply', 'operation', 'performance'],
                                ['power', 'supply', 'design', 'features'], ['power', 'supply', 'miscellaneous'],
                                ['keyboard', 'design', 'features'], ['keyboard', 'general'], ['keyboard', 'usability'],
                                ['keyboard', 'quality'], ['keyboard', 'operation', 'performance'],
                                ['mouse', 'design', 'features'], ['mouse', 'quality'],
                                ['mouse', 'operation', 'performance'],
                                ['mouse', 'usability'], ['mouse', 'general'],
                                ['fans', 'cooling', 'design', 'features'], ['fans', 'cooling', 'quality'],
                                ['fans', 'cooling', 'operation', 'performance'],
                                ['optical', 'drives', 'quality'], ['optical', 'drives', 'operation', 'performance'],
                                ['ports', 'quality'], ['ports', 'design', 'features'],
                                ['ports', 'operation', 'performance'],
                                ['graphics', 'quality'], ['graphics', 'general'], ['graphics', 'design_features'],
                                ['graphics', 'miscellaneous'],
                                ['multimedia', 'devices', 'usability'], ['multimedia', 'devices', 'miscellaneous'],
                                ['multimedia', 'devices', 'operation', 'performance'],
                                ['multimedia', 'devices', 'quality'],
                                ['multimedia', 'devices', 'general'], ['multimedia', 'devices', 'design', 'features'],
                                ['hardware', 'quality'], ['hardware', 'general'],
                                ['hardware', 'operation', 'performance'],
                                ['os', 'design', 'features'], ['os', 'general'], ['os', 'usability'],
                                ['os', 'miscellaneous'],
                                ['os', 'operation', 'performance'], ['os', 'quality'],
                                ['software', 'miscellaneous'], ['software', 'general'], ['software', 'quality'],
                                ['software', 'usability'], ['software', 'design', 'features'],
                                ['software', 'operation', 'performance'], ['software', 'price'],
                                ['warranty', 'general'], ['warranty', 'price'],
                                ['shipping', 'quality'], ['shipping', 'price'],
                                ['support', 'quality'], ['support', 'miscellaneous'], ['support', 'price'],
                                ['company', 'general']]

LAPTOPS_ASPECT_WORD_INDEX_MAP = {
    'laptopgeneral': 0,
    'laptopprice': 1,
    'laptopquality': 2,
    'laptopoperationperformance': 3,
    'laptopusability': 4,
    'laptopdesignfeatures': 5,
    'laptopportability': 6,
    'laptopconnectivity': 7,
    'laptopmiscellaneous': 8,
    'displaygeneral': 9,
    'displayquality': 10,
    'displayoperationperformance': 11,
    'displayusability': 12,
    'displaydesignfeatures': 13,
    'displayportability': 14,
    'displaymiscellaneous': 15,
    'cpugeneral': 16,
    'cpuprice': 17,
    'cpuquality': 18,
    'cpuoperationperformance': 19,
    'cpudesignfeatures': 20,
    'cpumiscellaneous': 21,
    'motherboardgeneral': 22,
    'motherboardprice': 23,
    'motherboardquality': 24,
    'motherboarddesignfeatures': 25,
    'motherboardmiscellaneous': 26,
    'harddiscgeneral': 27,
    'harddiscprice': 28,
    'harddiscquality': 29,
    'harddiscoperationperformance': 30,
    'harddiscdesignfeatures': 31,
    'harddiscmiscellaneous': 32,
    'memorygeneral': 33,
    'memoryprice': 34,
    'memorydesignfeatures': 35,
    'memorymiscellaneous': 36,
    'batterygeneral': 37,
    'batteryquality': 38,
    'batteryoperationperformance': 39,
    'batterydesignfeatures': 40,
    'batterymiscellaneous': 41,
    'powersupplygeneral': 42,
    'powersupplyprice': 43,
    'powersupplyquality': 44,
    'powersupplyoperationperformance': 45,
    'powersupplydesignfeatures': 46,
    'powersupplymiscellaneous': 47,
    'keyboardgeneral': 48,
    'keyboardquality': 49,
    'keyboardoperationperformance': 50,
    'keyboardusability': 51,
    'keyboarddesignfeatures': 52,
    'keyboardmiscellaneous': 53,
    'mousegeneral': 54,
    'mousequality': 55,
    'mouseoperationperformance': 56,
    'mouseusability': 57,
    'mousedesignfeatures': 58,
    'mousemiscellaneous': 59,
    'fanscoolinggeneral': 60,
    'fanscoolingquality': 61,
    'fanscoolingoperationperformance': 62,
    'fanscoolingdesignfeatures': 63,
    'fanscoolingmiscellaneous': 64,
    'opticaldrivesgeneral': 65,
    'opticaldrivesquality': 66,
    'opticaldrivesoperationperformance': 67,
    'opticaldrivesdesignfeatures': 68,
    'opticaldrivesmiscellaneous': 69,
    'portsgeneral': 70,
    'portsquality': 71,
    'portsoperationperformance': 72,
    'portsdesignfeatures': 73,
    'portsmiscellaneous': 74,
    'graphicsgeneral': 75,
    'graphicsquality': 76,
    'graphicsdesignfeatures': 77,
    'graphicsmiscellaneous': 78,
    'multimediadevicesgeneral': 79,
    'multimediadevicesquality': 80,
    'multimediadevicesoperationperformance': 81,
    'multimediadevicesusability': 82,
    'multimediadevicesdesignfeatures': 83,
    'multimediadevicesmiscellaneous': 84,
    'hardwaregeneral': 85,
    'hardwarequality': 86,
    'hardwareoperationperformance': 87,
    'hardwareusability': 88,
    'hardwaredesignfeatures': 89,
    'hardwaremiscellaneous': 90,
    'osgeneral': 91,
    'osquality': 92,
    'osoperationperformance': 93,
    'osusability': 94,
    'osdesignfeatures': 95,
    'osmiscellaneous': 96,
    'softwaregeneral': 97,
    'softwareprice': 98,
    'softwarequality': 99,
    'softwareoperationperformance': 100,
    'softwareusability': 101,
    'softwaredesignfeatures': 102,
    'softwaremiscellaneous': 103,
    'warrantygeneral': 104,
    'warrantyprice': 105,
    'warrantymiscellaneous': 106,
    'shippinggeneral': 107,
    'shippingprice': 108,
    'shippingquality': 109,
    'shippingmiscellaneous': 110,
    'supportgeneral': 111,
    'supportprice': 112,
    'supportquality': 113,
    'supportmiscellaneous': 114,
    'companygeneral': 115,
    'none': 116
}

LAPTOPS_INDEX_TO_ASPECT_WORD_MAP = {
    0: 'laptopgeneral',
    1: 'laptopprice',
    2: 'laptopquality',
    3: 'laptopoperationperformance',
    4: 'laptopusability',
    5: 'laptopdesignfeatures',
    6: 'laptopportability',
    7: 'laptopconnectivity',
    8: 'laptopmiscellaneous',
    9: 'displaygeneral',
    10: 'displayquality',
    11: 'displayoperationperformance',
    12: 'displayusability',
    13: 'displaydesignfeatures',
    14: 'displayportability',
    15: 'displaymiscellaneous',
    16: 'cpugeneral',
    17: 'cpuprice',
    18: 'cpuquality',
    19: 'cpuoperationperformance',
    20: 'cpudesignfeatures',
    21: 'cpumiscellaneous',
    22: 'motherboardgeneral',
    23: 'motherboardprice',
    24: 'motherboardquality',
    25: 'motherboarddesignfeatures',
    26: 'motherboardmiscellaneous',
    27: 'harddiscgeneral',
    28: 'harddiscprice',
    29: 'harddiscquality',
    30: 'harddiscoperationperformance',
    31: 'harddiscdesignfeatures',
    32: 'harddiscmiscellaneous',
    33: 'memorygeneral',
    34: 'memoryprice',
    35: 'memorydesignfeatures',
    36: 'memorymiscellaneous',
    37: 'batterygeneral',
    38: 'batteryquality',
    39: 'batteryoperationperformance',
    40: 'batterydesignfeatures',
    41: 'batterymiscellaneous',
    42: 'powersupplygeneral',
    43: 'powersupplyprice',
    44: 'powersupplyquality',
    45: 'powersupplyoperationperformance',
    46: 'powersupplydesignfeatures',
    47: 'powersupplymiscellaneous',
    48: 'keyboardgeneral',
    49: 'keyboardquality',
    50: 'keyboardoperationperformance',
    51: 'keyboardusability',
    52: 'keyboarddesignfeatures',
    53: 'keyboardmiscellaneous',
    54: 'mousegeneral',
    55: 'mousequality',
    56: 'mouseoperationperformance',
    57: 'mouseusability',
    58: 'mousedesignfeatures',
    59: 'mousemiscellaneous',
    60: 'fanscoolinggeneral',
    61: 'fanscoolingquality',
    62: 'fanscoolingoperationperformance',
    63: 'fanscoolingdesignfeatures',
    64: 'fanscoolingmiscellaneous',
    65: 'opticaldrivesgeneral',
    66: 'opticaldrivesquality',
    67: 'opticaldrivesoperationperformance',
    68: 'opticaldrivesdesignfeatures',
    69: 'opticaldrivesmiscellaneous',
    70: 'portsgeneral',
    71: 'portsquality',
    72: 'portsoperationperformance',
    73: 'portsdesignfeatures',
    74: 'portsmiscellaneous',
    75: 'graphicsgeneral',
    76: 'graphicsquality',
    77: 'graphicsdesignfeatures',
    78: 'graphicsmiscellaneous',
    79: 'multimediadevicesgeneral',
    80: 'multimediadevicesquality',
    81: 'multimediadevicesoperationperformance',
    82: 'multimediadevicesusability',
    83: 'multimediadevicesdesignfeatures',
    84: 'multimediadevicesmiscellaneous',
    85: 'hardwaregeneral',
    86: 'hardwarequality',
    87: 'hardwareoperationperformance',
    88: 'hardwareusability',
    89: 'hardwaredesignfeatures',
    90: 'hardwaremiscellaneous',
    91: 'osgeneral',
    92: 'osquality',
    93: 'osoperationperformance',
    94: 'osusability',
    95: 'osdesignfeatures',
    96: 'osmiscellaneous',
    97: 'softwaregeneral',
    98: 'softwareprice',
    99: 'softwarequality',
    100: 'softwareoperationperformance',
    101: 'softwareusability',
    102: 'softwaredesignfeatures',
    103: 'softwaremiscellaneous',
    104: 'warrantygeneral',
    105: 'warrantyprice',
    106: 'warrantymiscellaneous',
    107: 'shippinggeneral',
    108: 'shippingprice',
    109: 'shippingquality',
    110: 'shippingmiscellaneous',
    111: 'supportgeneral',
    112: 'supportprice',
    113: 'supportquality',
    114: 'supportmiscellaneous',
    115: 'companygeneral',
    116: 'none'
}


def build_word_frequency_distribution():
    """
    1. Extract tokens from the review text
    2. Calculate frequency of each token
    3. Create a freq dict and store it in a file

    :return: A dict of <token, freq>
    """
    try:
        freq_dist_f = read_binary(WORD_FREQ_FILE)
        print('frequency distribution loaded')
        return freq_dist_f
    except IOError:
        pass

    print('building frequency distribution')
    freq = defaultdict(int)
    if FILE_NAME == 'restaurant':
        for aspect_word in RESTAURANT_ASPECT_WORDS:
            freq[aspect_word] += 1
    elif FILE_NAME == 'laptops':
        for aspect_word in LAPTOPS_ASPECT_WORDS:
            freq[aspect_word] += 1

    files = [FORMATTED_FILE_NAME]
    if EMBEDDING_TYPE == 'fasttext':
        files.append(FORMATTED_FILE_NAME.replace('train', 'test'))
        files.append(FORMATTED_FILE_NAME.replace('train', 'val'))

    for file_path in files:
        print('building vocab from file - ' + file_path)
        for i, review in enumerate(read_binary(file_path)):
            sentences = review[1]

            for sent in sentences:
                tokens = NLP.tokenizer(sent[0])
                for token in tokens:
                    freq[token.orth_] += 1
                if i % 100 == 0:
                    write_binary(freq, WORD_FREQ_FILE)
                    print('dump at {}'.format(i))
            write_binary(freq, WORD_FREQ_FILE)
    return freq


def build_vocabulary(lower = 1, n = MAX_VOCAB_SIZE):
    """
    1. Get word frequency distribution
    2. Sort is based on word frequencies
    3. Make a vocab dist using the most frequent words
    4. Store vocab dist in a file in format <word, identifier>

    :param lower: Identifiers below this are reserved
    :param n: Number of unique expected words
    :return: A dict of vocabulary words and an assigned identifier
    """

    try:
        vocab_to_code = read_binary(VOCAB_TO_CODE_FILE)
        code_to_vocab = read_binary(CODE_TO_VOCAB_FILE)
        print('vocabulary loaded')
        return vocab_to_code, code_to_vocab
    except IOError:
        print('building vocabulary')
    freq = build_word_frequency_distribution()

    # get glove embeddings
    print('loading embeddings')
    if EMBEDDING_TYPE == 'glove':
        word_to_embeddings = load_glove_embeddings()
    elif EMBEDDING_TYPE == 'fasttext':
        word_to_embeddings = load_oov_fastText_embeddings()
    else:
        word_to_embeddings = {}

    # sorting words in ascending order based on frequency and then pick top n words
    top_words = list(sorted(freq.items(), key = lambda x: -x[1]))[:n - lower + 1]
    # create optimum vocab size
    print('Vocab count : ' + str(len(top_words)))
    # global MAX_VOCAB_SIZE
    # global UNKNOWN
    max_vocab_size = len(top_words) + 2
    unknown = max_vocab_size - 1
    vocab_to_code = {}
    code_to_vocab = {}

    # an array of embeddings with index referring to the vocab code. First and last index is
    # reserved for padding and unknown words respectively.
    code_to_embed = np.zeros(shape = (max_vocab_size, EMBEDDING_DIMENSION), dtype = np.float32)
    code_to_embed[PAD] = PAD_EMBEDDING
    code_to_embed[unknown] = UNKNOWN_EMBEDDING
    vocab_to_code['<UNK>'] = unknown
    code_to_vocab[unknown] = '<UNK>'
    vocab_to_code['<PAD>'] = PAD
    code_to_vocab[PAD] = '<PAD>'

    # lower vocab indexes are reserved for padding and unknown words
    i = lower
    for w, freq in top_words:
        vocab_to_code[w] = i
        code_to_vocab[i] = w
        try:
            if EMBEDDING_TYPE == 'glove':
                embedding = word_to_embeddings.word_vec(w)
            elif EMBEDDING_TYPE == 'fasttext':
                embedding = word_to_embeddings.get_word_vector(w)
        except KeyError:
            embedding = UNKNOWN_EMBEDDING

        if EMBEDDING_TYPE in ['glove', 'fasttext']:
            code_to_embed[i] = embedding
        i += 1
    write_binary(vocab_to_code, VOCAB_TO_CODE_FILE)
    write_binary(code_to_vocab, CODE_TO_VOCAB_FILE)
    write_binary(code_to_embed, CODE_TO_EMBED_FILE)
    return vocab_to_code, code_to_vocab


def get_uncoded_data(code_to_vocab, datapoint):
    aspect_words = []
    review = []
    aspect_codes = datapoint[0]
    coded_sentences = datapoint[1]
    polarities = datapoint[2]

    for aspect_code in aspect_codes:
        aspect_words.append(code_to_vocab.get(aspect_code))

    for sentence in coded_sentences:
        sent_words = []
        for coded_word in sentence:
            sent_words.append(code_to_vocab.get(coded_word))
        review.append(sent_words)
    x = [aspect_words, review, polarities]
    return x


def process_data():
    vocab_to_code, code_to_vocab = build_vocabulary()
    max_vocab_size = len(vocab_to_code)
    unknown = max_vocab_size - 1
    print('Final Vocab Size : ' + str(max_vocab_size))
    try:
        coded_dataset = []
        for i, review in enumerate(read_binary(FORMATTED_FILE_NAME)):
            coded_aspect = []
            coded_sentences = []

            if i == 0:
                print(review)

            sentences = review[1]
            aspect_words = review[0]
            polarities = review[2]

            for aspect_word in aspect_words:
                coded_aspect.append(vocab_to_code.get(aspect_word, unknown))

            for sent in sentences:
                coded_sentence = []
                tokens = NLP.tokenizer(sent[0])
                for token in tokens:
                    coded_sentence.append(vocab_to_code.get(token.orth_, unknown))
                coded_sentences.append(coded_sentence)

            coded_review = [coded_aspect, coded_sentences, polarities]

            # dataset
            coded_dataset.append(coded_review)
            write_binary(coded_dataset, PROCESSED_FILE_NAME)
            print('dump at {}'.format(i))

        datapoint = coded_dataset[0]
        print(datapoint)
        print(get_uncoded_data(code_to_vocab, datapoint))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    process_data()
