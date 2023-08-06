import sys
from collections import Counter
from copy import deepcopy
from datetime import timedelta

import pandas as pd
from numpy import unique

from ..common import general_utils
from ..common.nlp_utils import STTM, CleanText, Features, Polarity

ERR_SYS = "\nSystem error: "


class STTMgroupsTW:
    """
    This class groups texts into groups of similar topics.
    """

    def __init__(self, df_replies, account_ids=[], account_names=[]):
        """
        This method computes the DataFrame 'df_replies_full'
        which contains all the information of the twitter replies, including column 'group' and 'polarity'.

        Parameters
        ----------
        df_replies:
            type: DataFrame
            Information of the tweets or the twitter replies.
            This Pandas DataFrame must have columns 'text', 'twitter_id', 'screen_name',  and 'replying_to_id' and 'replying_to' if the data frame contains tweet replies.
        df_users:
            type: DataFrame
            Information of the twitter users.
        groups:
            type: dict
            Maps the groups (client, competition, archetype, trends) to the
            corresponding page ids for each group.
        """
        METHOD_NAME = "__init__"
        df_replies_full = deepcopy(df_replies)
        self.df_replies_full = df_replies_full
        # self.groups = groups
        try:
            if "replying_to" in self.df_replies_full.keys():
                self.df_replies_full["name"] = self.df_replies_full["replying_to"]

            else:
                self.df_replies_full["name"] = self.df_replies_full["screen_name"]
            self.df_replies_full["all"] = "all groups"

        except Exception as e:
            print(e)
            error_1 = sys.exc_info()[0]
            print(ERR_SYS + str(error_1))
            print(f"Class: {self.__str__()}\nMethod: {METHOD_NAME}")
            print(
                "Warning: Class: {self.__str__()}\nMethod: {METHOD_NAME}' no 'replying_to' or 'screen_name' column in DataFrame"
            )
            if "name" not in self.df_replies_full.keys():
                self.df_replies_full["name"] = "no name"

        if account_ids:
            self.df_replies_full = self.df_replies_full[
                self.df_replies_full.replying_to_id.isin(account_ids)
            ]
        elif account_names:
            self.df_replies_full = self.df_replies_full[
                self.df_replies_full.name.isin(account_names)
            ]

        try:
            if df_replies.empty:
                print("Warning: input data DataFrame is empty.")
        except Exception as e:
            print(e)
            error_1 = sys.exc_info()[0]
            print(ERR_SYS + str(error_1))
            print(f"Class: {self.__str__()}\nMethod: {METHOD_NAME}")
            self.df_replies_full = pd.DataFrame(columns=[""])

    def remove_from_text(self, text, toremove):
        text_copy = deepcopy(text)
        for word in text:
            if word in toremove:
                text_copy.remove(word)
        return text_copy

    def get_sttm_groups(self, with_remove=False, list_remove=[], min_texts=100):
        METHOD_NAME = "get_sttm_groups"

        try:

            # cleaning text:
            if "processed_text" not in self.df_replies_full.keys():
                self.df_replies_full["processed_text"] = self.df_replies_full[
                    "text"
                ].apply(
                    lambda msg: CleanText(msg).process_text(
                        mentions=True, hashtags=True, links=True, spec_chars=True
                    )
                )

            # drop empty replies
            self.df_replies_full = self.df_replies_full.dropna(
                subset=["processed_text"]
            )
            self.df_replies_full = self.df_replies_full.drop(
                self.df_replies_full[self.df_replies_full["processed_text"] == ""].index
            )

            if list_remove:
                # self.df_replies_full['processed_text'] = self.df_replies_full['processed_text'].(lambda x: json.loads(x))
                self.df_replies_full["processed_text"] = self.df_replies_full[
                    "processed_text"
                ].apply(lambda x: str(x).split(" "))
                self.df_replies_full["processed_text"] = self.df_replies_full[
                    "processed_text"
                ].apply(lambda x: self.remove_from_text(x, list_remove))
                self.df_replies_full["processed_text"] = self.df_replies_full[
                    "processed_text"
                ].apply(lambda msg: str(msg))

            # getting the polarity of the clean text
            if "polarity" not in self.df_replies_full.keys():
                self.df_replies_full = Polarity().polarity(df_text=self.df_replies_full)

            # tokenized text:
            if "tokenized_text" not in self.df_replies_full.keys():
                getfeatures = Features()
                self.df_replies_full[
                    "tokenized_text"
                ] = self.df_replies_full.processed_text.apply(
                    lambda msg: getfeatures.pos_tags(msg)["words"]
                )

            # drop empty comments
            self.df_replies_full = self.df_replies_full.dropna(
                subset=["tokenized_text"]
            )
            self.df_replies_full = self.df_replies_full.drop(
                self.df_replies_full[self.df_replies_full["tokenized_text"] == ""].index
            )
            self.df_replies_full[
                "len_text"
            ] = self.df_replies_full.tokenized_text.apply(lambda msg: len(msg))
            self.df_replies_full = self.df_replies_full[
                self.df_replies_full["len_text"] != 0
            ]

            # getting sttm groups
            if self.df_replies_full.tokenized_text.shape[0] > min_texts:
                self.df_replies_full = STTM(self.df_replies_full).sttm_model()
            else:
                print(
                    "warning: in",
                    f"Class: {self.__str__()}\nMethod: {METHOD_NAME}",
                    "not enough texts in DataFrame for STTM grouping. Returning value 1 for group column for sttm_group",
                )
                self.df_replies_full["sttm_group"] = 1

        except Exception as e:
            print(e)
            error_1 = sys.exc_info()[0]
            print(ERR_SYS + str(error_1))
            print(f"Class: {self.__str__()}\nMethod: {METHOD_NAME}")
            if "polarity" not in self.df_replies_full.keys():
                self.df_replies_full["polarity"] = ""
            if "sttm_group" not in self.df_replies_full.keys():
                self.df_replies_full["sttm_group"] = ""

    def get_sttm_groups_withremove(
        self, df_preprocessed_sttm, list_toremove=[], min_texts=100
    ):
        METHOD_NAME = "get_sttm_groups_withremove"
        self.df_preprocessed_sttm = deepcopy(df_preprocessed_sttm)

        try:
            # self.df_preprocessed_sttm['tokenized_text'] = self.df_preprocessed_sttm['tokenized_text'].apply(lambda x: json.loads(x))
            self.df_preprocessed_sttm["tokenized_text"] = self.df_preprocessed_sttm[
                "tokenized_text"
            ].apply(lambda x: x[2:-2])
            self.df_preprocessed_sttm["tokenized_text"] = self.df_preprocessed_sttm[
                "tokenized_text"
            ].apply(lambda x: str(x).split("', '"))

            self.df_preprocessed_sttm["tokenized_text"] = self.df_preprocessed_sttm[
                "tokenized_text"
            ].apply(lambda x: self.remove_from_text(x, list_toremove))

            # drop empty comments
            self.df_preprocessed_sttm = self.df_preprocessed_sttm.dropna(
                subset=["tokenized_text"]
            )
            self.df_preprocessed_sttm = self.df_preprocessed_sttm.drop(
                self.df_preprocessed_sttm[
                    self.df_preprocessed_sttm["tokenized_text"] == ""
                ].index
            )
            self.df_preprocessed_sttm = self.df_preprocessed_sttm.drop(
                self.df_preprocessed_sttm[
                    self.df_preprocessed_sttm["tokenized_text"] == " "
                ].index
            )
            self.df_preprocessed_sttm[
                "len_text"
            ] = self.df_preprocessed_sttm.tokenized_text.apply(lambda msg: len(msg))
            self.df_preprocessed_sttm = self.df_preprocessed_sttm[
                self.df_preprocessed_sttm["len_text"] != 0
            ]

            # getting sttm groups
            if self.df_preprocessed_sttm.tokenized_text.shape[0] > min_texts:
                self.df_preprocessed_sttm = STTM(self.df_preprocessed_sttm).sttm_model()
            else:
                print(
                    "warning: in",
                    f"Class: {self.__str__()}\nMethod: {METHOD_NAME}",
                    "\n Not enough texts in DataFrame for STTM grouping. Returning value 1 for group column for sttm_group",
                )
                self.df_preprocessed_sttm["sttm_group"] = 1

        except Exception as e:
            print(e)
            error_1 = sys.exc_info()[0]
            print(ERR_SYS + str(error_1))
            print(f"Class: {self.__str__()}\nMethod: {METHOD_NAME}")
            self.df_preprocessed_sttm["sttm_group"] = ""

    def counter_of_words(self, words, mention, n_words=10):
        """
        Counts the elements in the list 'words' and returns
        the 'n_words' most frequent.

        Parameters
        ----------
        words
            type: list
            List of words to count.
        mention:
            type: str
            Mention to delete from the counter to avoid overcounting
            mentions in responses to a certain account.
        n_words:
            type: int
            Number of most frequent words to return

        Returns
        -------
        dict
        """

        counter = Counter(words)
        try:
            del counter["@" + mention.lower()]
        except Exception:
            pass
        return dict(counter.most_common(n_words))

    def get_percentage(self, counter):
        """
        Computes the frequency (percentage) of the elements in the
        dictionary 'counter'.

        Parameters
        ----------
        counter
            type: dict
            Dictionary of elements to count.

        Returns
        -------
        dict
        """

        percentage = Counter(counter)
        percentage = dict(
            [
                (i, perc / sum(percentage.values()) * 100.0)
                for i, perc in percentage.most_common()
            ]
        )
        return percentage

    def message_to_group_columns(self):
        """
        This function constructs the columns to group the dataframe
        'data' for audiencies visualizations.

        Returns
        -------
        DataFrame
        """

        data_texts = deepcopy(self.df_replies_full)

        if "__date_cot" not in data_texts.keys():
            data_texts["__date_cot"] = pd.to_datetime(
                data_texts["created_at"]
            ) - timedelta(hours=5)

        if "replying_to" in data_texts.keys():
            data_texts = data_texts[
                [
                    "sttm_group",
                    "tokenized_text",
                    "replying_to",
                    "__date_cot",
                    "polarity",
                ]
            ]
            data_texts = data_texts.rename(columns={"replying_to": "__mention"})
        else:
            data_texts = data_texts[
                ["sttm_group", "tokenized_text", "__date_cot", "polarity"]
            ]
            data_texts["__mention"] = ""

        self.data_texts = data_texts

    def get_grouped_dataframe(self):
        """
        Groups the DataFrame 'data' into a DataFrame containing information
        abput the groups of texts.

        Parameters
        ----------
        data
            type: DataFrame
            DataFrame containing information about the texts.

        Returns
        -------
        DataFrame
        """
        data_grouped = deepcopy(
            self.data_texts[
                ["sttm_group", "tokenized_text", "__mention", "__date_cot", "polarity"]
            ]
        )

        data_grouped["polarity"] = data_grouped["polarity"].apply(lambda pol: str(pol))

        data_grouped["__weekday"] = data_grouped["__date_cot"].apply(
            lambda d: d.strftime("%A")
        )

        data_grouped["__n_docs"] = 1

        data_grouped = (
            data_grouped[
                [
                    "sttm_group",
                    "__n_docs",
                    "tokenized_text",
                    "__mention",
                    "__weekday",
                    "polarity",
                ]
            ]
            .groupby("sttm_group")
            .agg(
                {
                    "__n_docs": "count",
                    "tokenized_text": "sum",
                    "__mention": "last",
                    "__weekday": lambda x: ",".join(x)
                    if len(unique(data_grouped["__weekday"])) > 1
                    else "",
                    "polarity": lambda x: ",".join(x),
                }
            )
        )

        data_grouped["__percentage"] = (
            data_grouped["__n_docs"] * 100 / sum(data_grouped["__n_docs"])
        )

        data_grouped = data_grouped.rename(columns={"tokenized_text": "__words"})

        data_grouped["__words"] = data_grouped.apply(
            lambda row: self.counter_of_words(row["__words"], row["__mention"]), axis=1
        )
        data_grouped = data_grouped.drop(columns=["__mention"])

        data_grouped["__weekday"] = data_grouped["__weekday"].apply(
            lambda wd: wd.split(",")
        )
        data_grouped = data_grouped.rename(columns={"__weekday": "__presence"})
        data_grouped["__presence"] = data_grouped["__presence"].apply(
            lambda p: self.get_percentage(p)
        )

        data_grouped["polarity"] = data_grouped["polarity"].apply(
            lambda wd: wd.split(",")
        )
        data_grouped = data_grouped.rename(
            columns={"polarity": "__polarity_distribution"}
        )
        data_grouped["__polarity_distribution"] = data_grouped[
            "__polarity_distribution"
        ].apply(lambda p: self.get_percentage(p))

        data_grouped = data_grouped.reset_index().sort_values(
            "__percentage", ascending=False
        )

        return data_grouped
