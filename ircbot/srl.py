from enum import Enum
import os
from allennlp.predictors.predictor import Predictor
import allennlp_models.syntax.srl


def get_predictor():
    if "bert-base-srl-2020.03.24.tar.gz" in os.listdir():
        print("SUCCESS: found `bert-base-srl-2020.03.24.tar.gz` in current directory")
        BERT_SRL_MODEL_PATH = "bert-base-srl-2020.03.24.tar.gz"
    else:
        print("WARNING: failed to find `bert-base-srl-2020.03.24.tar.gz` in current directory")
        print("WARNING: downloading from allennlp's public models storage")
        BERT_SRL_MODEL_PATH = "https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.03.24.tar.gz"

    print("BERT_SRL_MODEL_PATH: ", BERT_SRL_MODEL_PATH)
    print("os.getcwd(): ", os.getcwd())
    predictor = Predictor.from_path(BERT_SRL_MODEL_PATH)
    return predictor


class SRL_TAGS(Enum):
    """
    > The Arg0 label is assigned to arguments which are understood as agents, causers, or experiencers.
    > The Arg1 label is usually assigned to the patient argument,
    > i.e. the argument which undergoes the change of state or is being affected by the action.

    > Frameset leave.01 "move away from":
    >     Arg0: entity leaving
    >     Arg1: place left

    > Frameset leave.02 "give":
    >     Arg0: giver
    >     Arg1: thing given
    >     Arg2: beneficiary

    > In general, if an argument satisfies two roles,
    > the highest ranked argument label should be selected,
    > where Arg0 >> Arg1 >> Arg2>>... .

    > 1.4.13 Modals (MOD)
    > Modals are: will, may, can, must, shall, might, should, could, would.
    > These elements are consistently labeled in the TreeBank as ‘MOD.’
    > These are one of the few elements that are selected and tagged directly on the modal word itself,
    > as opposed to selecting a higher node that contains the lexical item.

    References:
    * https://github.com/allenai/allennlp-models/blob/d2b50dff8daa40afb577feea0a9778c3438fdbe2/test_fixtures/syntax/srl/serialization/vocabulary/labels.txt
    * https://catalog.ldc.upenn.edu/docs/LDC2007T21/propbank/english-propbank.pdf
    * https://www.aclweb.org/anthology/J05-1004/
    * https://www.aclweb.org/anthology/W12-4501/
    * https://www.aclweb.org/anthology/P15-4009/
    """

    NO_TAG = "O"

    BEGIN_VERB = "B-V"
    VERB = "V"

    BEGIN_AGENT = BEGIN_ARG0 = "B-ARG0"
    INTERM_AGENT = INTERM_ARG0 = "I-ARG0"
    AGENT = ARG0 = "ARG0"

    BEGIN_PATIENT = BEGIN_ARG1 = "B-ARG1"
    INTERM_PATIENT = INTERM_ARG1 = "I-ARG1"
    PATIENT = ARG1 = "ARG1"

    BEGIN_ARG2 = "B-ARG2"
    INTERM_ARG2 = "I-ARG2"
    ARG2 = "ARG2"

    BEGIN_ARG3 = "B-ARG3"
    INTERM_ARG3 = "I-ARG3"
    ARG3 = "ARG3"

    ARG4 = "ARG4"

    ARGM_ADJ = "ARGM-ADJ"

    ARGM_EXT = "ARGM-EXT"

    C_ARG0 = "C-ARG0"
    C_ARG1 = "C-ARG1"
    C_ARG2 = "C-ARG2"

    ARGM_LOC = "ARGM-LOC"

    ARGM_PNC = "ARGM-PNC"

    ARGM_CAU = "ARGM-CAU"

    ARGM_DIR = "ARGM-DIR"

    ARGM_LVB = "ARGM-LVB"

    ARGM_COM = "ARGM-COM"
    R_ARG3 = "R-ARG3"
    ARGM_REC = "ARGM-REC"
    ARG5 = "ARG5"
    C_ARGM_MNR = "C-ARGM-MNR"

    R_ARGM_TMP = "R-ARGM-TMP"

    R_ARGM_CAU = "R-ARGM-CAU"

    BEGIN_TEMPORAL_MARKER = "B-ARGM-TMP"
    INTERM_TEMPORAL_MARKER = "I-ARGM-TMP"
    TEMPORAL = TEMPORAL_MARKER = ARG_TMP = "ARGM-TMP"

    # Transition words like "But" or "Also" or "However"
    # Could also be a name like "Vince" >> e.g. "I aint kidding you, Vince."
    BEGIN_DISCOURSE_MARKER = "B-ARGM-DIS"
    INTERM_DISCOURSE_MARKER = "I-ARGM-DIS"
    DISCOURSE = DISCOURSE_MARKER = ARGM_DIS = "ARGM-DIS"

    BEGIN_NEGATION_MARKER = "B-ARGM-NEG"
    NEGATION = NEGATION_MARKER = ARGM_NEG = "ARGM-NEG"

    # Modals are: will, may, can, must, shall, might, should, could, would
    # It may be useful to enforce this by `assert` statements in code
    # sometimes the SRL Predictor tags "can" as "VERB" when it should be MOD
    # but BE CAREFUL.. it is possible "to can" and "to be canned"
    BEGIN_MODAL = "B-ARGM-MOD"
    MODAL = MODAL_MARKER = ARGM_MOD = "ARGM-MOD"

    BEGIN_MANNER_MARKER = "B-ARGM-MNR"
    INTERM_MANNER_MARKER = "I-ARGM-MNR"
    MANNER = MANNER_MARKER = ARGM_MNR = "ARGM-MNR"

    BEGIN_ADVERBIAL_MARKER = "B-ARGM-ADV"
    INTERM_ADVERBIAL_MARKER = "I-ARGM-ADV"
    ADVERBIAL = ADVERBIAL_MARKER = ARGM_ADV = "ARGM-ADV"

    BEGIN_PURPOSE_MARKER = "B-ARGM-PRP"
    INTERM_PURPOSE_MARKER = "I-ARGM-PRP"
    PURPOSE = PURPOSE_MARKER = ARGM_PRP = "ARGM-PRP"

    BEGIN_GOAL_MARKER = BEGIN_ARGM_GOL = "B-ARGM-GOL"
    INTERM_GOAL_MARKER = INTERM_ARGM_GOL = "I-ARGM-GOL"
    GOAL = GOAL_MARKER = ARGM_GOL = "ARGM-GOL"

    BEGIN_REFERENTIAL_AGENT = BEGIN_R_ARG0 = "B-R-ARG0"
    REF_AGENT = REFERENTIAL_AGENT = R_ARG0 = "R-ARG0"

    BEGIN_REFERENTIAL_PATIENT = BEGIN_R_ARG1 = "B-R-ARG1"
    REF_PATIENT = REFERENTIAL_PATIENT = R_ARG1 = "R-ARG1"

    BEGIN_REFERENTIAL_ARG2 = BEGIN_R_ARG2 = "B-R-ARG2"
    R_ARG2 = "R-ARG2"

    R_ARGM_MNR = "R-ARGM-MNR"

    R_ARGM_LOC = "R-ARGM-LOC"

    # > Pierre Vinken , 61 years old ,
    # > will join the board as a nonexecutive director Nov. 29 .
    # ARG0: Pierre Vinken , 61 years old ,
    # ARGM-MOD: will
    # REL: join
    # ARG1: the board
    # ARGM-PRD: as a nonexecutive director
    # ARGM-TMP: Nov. 29
    PREDICATE_MODIFIER = ARGM_PRD = "ARGM-PRD"
