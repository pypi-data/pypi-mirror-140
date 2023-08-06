import pandas as pd
from collections import defaultdict
import logging
logging.basicConfig(level = logging.INFO)

class pass_data():
    def __init__(self, data: object, target_column: str):
        self.target_column = target_column
        self.data = data

    def use_preprocessor(self, preprocessor: str = "base", custom: list = None, special_token: list = ["[SEP]"]):
        preprocessor = preprocessor.lower()
        if preprocessor == "strong":
            output = self.preprocessor_strong()
        elif preprocessor == "base":
            output = self.preprocessor_base()
        elif preprocessor == "weak":
            output = self.preprocessor_weak()
        elif preprocessor == "custom":
            self.custom = custom
            self.special_token = special_token
            output = self.preprocessor_custom()
        return output

    def use_analyzer(self, analyzer: str = "base", custom: list = None):
        analyzer = analyzer.lower()
        if analyzer == "base":
            output = self.analyzer_base()
        return output

    def preprocessor_strong(self):
        fn_list = ["P_C_low", "P_R_nan", "P_R_spe", "P_R_123", "P_R_web", "P_R_@@@", "P_R_\\n", "P_R_WWW"]
        self.preprocessor_run(fn_list)
        return self.data
    
    def preprocessor_base(self):
        fn_list = ["P_G_WA1", "P_R_nan", "P_R_web", "P_R_@@@", "P_R_\\n", "P_R_WWW"]
        self.preprocessor_run(fn_list)
        return self.data

    def preprocessor_weak(self):
        fn_list = ["P_G_WA1", "P_R_nan", "P_R_\\n", "P_R_WWW"]
        self.preprocessor_run(fn_list)
        return self.data
    
    def preprocessor_custom(self):
        fn_list = self.custom
        self.preprocessor_run(fn_list)
        return self.data
    
    def preprocessor_run(self, fn_list):
        if "P_C_low" in fn_list:
            self.convert_lowercase()
        if "P_G_WA1" in fn_list:
            self.give_whitespace_alpha_number()
        if "P_R_nan" in fn_list:
            self.remove_nan()
        if "P_R_spe" in fn_list:
            self.remove_special_characters()
        if "P_R_123" in fn_list:
            self.remove_numbers()
        if "P_R_web" in fn_list:
            self.remove_website_links()
        if "P_R_@@@" in fn_list:
            self.remove_emails()
        if "P_R_\\n" in fn_list:
            self.remove_nextline()
        if "P_R_WWW" in fn_list:
            self.remove_repeating_whitespace()
        if "P_R_???" in fn_list:
            self.remove_special_token()

    def analyzer_base(self):
        analyzed_dict = defaultdict()
        analyzed_dict["each_word_counter"] = self.each_word_counter()
        return analyzed_dict

    """
    PREPROCESSOR FUNCTIONS START
    """
    def convert_lowercase(self):
        logging.info(f"Converting dataframe to lowercase in target column: {self.target_column}")
        self.data[self.target_column] = self.data[self.target_column].apply(lambda x: x.lower())

    def give_whitespace_alpha_number(self):
        logging.info(f"Give whitespace (when a character comes right after number, vice versa) to target column: {self.target_column}")
        self.data[self.target_column] = self.data[self.target_column].str.replace(r'(?<=([a-z])|\d)(?=(?(1)\d|[a-z]))', ' ', regex=True)

    def remove_nan(self):
        logging.info(f"Removing NaN from target column: {self.target_column}")
        self.data[self.target_column] = self.data[self.target_column].dropna()

    def remove_special_characters(self):
        logging.info(f"Removing special characters from target column: {self.target_column}")
        self.data[self.target_column] = self.data[self.target_column].str.replace(r'[^A-Za-z0-9 ]+', '', regex=True)

    def remove_numbers(self):
        logging.info(f"Removing numbers from target column: {self.target_column}")
        self.data[self.target_column] = self.data[self.target_column].str.replace(r'\d+',"", regex=True)
    
    def remove_website_links(self):
        logging.info(f"Removing website links from target column: {self.target_column}")
        self.data[self.target_column] = self.data[self.target_column].str.replace(r"http\S+", "", regex=True)

    def remove_emails(self):
        logging.info(f"Removing emails from target column: {self.target_column}")
        self.data[self.target_column] = self.data[self.target_column].str.replace(r"\S*@\S*\s?", "", regex=True)

    def remove_nextline(self):
        logging.info(f"Removing nextline from target column: {self.target_column}")
        self.data[self.target_column] = self.data[self.target_column].str.replace(r"\n", " ", regex=True)

    def remove_repeating_whitespace(self):
        logging.info(f"Removing repeating whitespace from target column: {self.target_column}")
        # replace more than 1 space with 1 space
        self.data[self.target_column] = self.data[self.target_column].str.replace(r"\s\s+", "", regex=True)
    
    def remove_special_token(self):
        logging.info(f"Removing special tokens from target column: {self.target_column}")
        for token in self.special_token:
            self.data[self.target_column] = self.data[self.target_column].str.replace(token, "", regex=False)
    """
    PREPROCESSOR FUNCTIONS END
    """
    """
    ANALYZER FUNCTIONS START
    """
    def each_word_counter(self) -> dict:
        logging.info("Counting each word")
        return dict(self.data[self.target_column].str.split().explode().value_counts())
    """
    ANALYZER FUNCTIONS END
    """
    