import sys
from copy import deepcopy
from datetime import timedelta

import numpy as np
import pandas as pd

from wj_analysis.twitter import polarity_distribution

ERR_SYS = "\nSystem error: "


class PolarityAnalysisTW:
    def __init__(self, df_sentiment):
        self.df_sentiment = df_sentiment

    def top_post(self, df_replies, threshold=10):
        METHOD_NAME = "posts"

        REPLIES_COLUMNS = [
            "in_reply_to_screen_name",
            "in_reply_to_user_id",
            "text",
            "in_reply_to_status_id",
        ]
        SENTIMENT_COLUMNS = ["post_id", "sentiment"]

        OUTPUT_COLUMNS = [
            "name",
            "page_id",
            "post_id",
            "message",
            "permalink_url",
            "sentiment",
            "rel_sentiment",
        ]

        if len(self.df_sentiment) > 0 and len(df_replies) > 0:
            try:
                df_getpolarity = deepcopy(df_replies[REPLIES_COLUMNS])
                df_getpolarity = df_getpolarity.rename(
                    columns={
                        "in_reply_to_screen_name": "name",
                        "text": "message",
                        "in_reply_to_status_id": "post_id",
                        "in_reply_to_user_id": "page_id",
                    }
                )
                df_getpolarity["sentiment"] = df_getpolarity["post_id"].map(
                    dict(self.df_sentiment[SENTIMENT_COLUMNS].values)
                )
                df_getpolarity = df_getpolarity.dropna(
                    subset=["sentiment"]
                ).reset_index(drop=True)
                df_getpolarity["count_comments"] = [
                    sum(polarity.values()) for polarity in df_getpolarity["sentiment"]
                ]
                df_getpolarity = df_getpolarity[df_getpolarity["count_comments"] >= 10]
                if len(df_getpolarity) > 0:
                    rel_polarity = []
                    for index, row in df_getpolarity.iterrows():
                        for key in row["sentiment"].keys():
                            row["sentiment"][key] /= row["count_comments"]
                        rel_polarity.append(
                            np.dot(
                                list(row["sentiment"].keys()),
                                list(row["sentiment"].values()),
                            )
                        )
                    df_getpolarity.insert(2, "rel_polarity", rel_polarity, True)
                    df_getpolarity = df_getpolarity[
                        df_getpolarity["rel_polarity"] > 0.1
                    ]
                    df_getpolarity["permalink_url"] = [
                        "twitter.com/user/status/{}".format(text)
                        for text in df_getpolarity["post_id"]
                    ]
                    return (
                        df_getpolarity.sort_values(by=["rel_polarity"], ascending=False)
                        .reset_index(drop=True)
                        .head(threshold)
                    )
                else:
                    print(
                        "Warning: no post has more than 10 comments, thus can't be analyze"
                    )
                    return pd.DataFrame(columns=OUTPUT_COLUMNS)
            except Exception as e:
                exception_type = sys.exc_info()[0]
                print(ERR_SYS + str(exception_type))
                print(e)
                print(f"Class: {self.__str__()}\nMethod: {METHOD_NAME}\n")
                return pd.DataFrame(columns=OUTPUT_COLUMNS)
        else:
            print("Warning: One of the DataFrames is empty. It cannot be computed.")
            self.df_getpolarity = pd.DataFrame(columns=OUTPUT_COLUMNS)
            self.len_getpolarity = len(self.df_getpolarity)

    def timeaccount_post(self):
        METHOD_NAME = "timeaccount_post"

        OUTPUT_COLUMNS = ["_object_id", "_object_name", "date", "day_sentiment"]

        if len(self.df_sentiment) > 0:
            try:
                self.df_sentiment["created_time"] = pd.to_datetime(
                    self.df_sentiment["created_time"]
                ) - timedelta(hours=5)
                self.df_sentiment["date"] = self.df_sentiment["created_time"].apply(
                    lambda d: d.date()
                )
                df_timeaccount = pd.DataFrame(columns=OUTPUT_COLUMNS)
                page_names = dict(
                    self.df_sentiment[["_object_id", "_object_name"]].values
                )
                for brand_id in self.df_sentiment["_object_id"].drop_duplicates():
                    df_brand = self.df_sentiment[
                        self.df_sentiment["_object_id"] == brand_id
                    ]
                    for date in df_brand["date"].drop_duplicates():
                        df_date = df_brand[df_brand["date"] == date]
                        day_sentiment = {
                            -1.0: 0.0,
                            -0.5: 0.0,
                            0.0: 0.0,
                            0.5: 0.0,
                            1.0: 0.0,
                        }
                        for dict_values in df_date["sentiment"]:
                            for key in np.arange(-1.0, 1.5, 0.5):
                                day_sentiment[key] += dict_values[key]
                        df_timeaccount.loc[len(df_timeaccount)] = [
                            brand_id,
                            page_names[brand_id],
                            date,
                            day_sentiment,
                        ]
                df_timeaccount["count_comments"] = [
                    sum(polarity.values())
                    for polarity in df_timeaccount["day_sentiment"]
                ]
                if len(df_timeaccount) > 0:
                    for index, row in df_timeaccount.iterrows():
                        for key in row["day_sentiment"].keys():
                            row["day_sentiment"][key] /= row["count_comments"]
                return df_timeaccount
            except Exception as e:
                exception_type = sys.exc_info()[0]
                print(ERR_SYS + str(exception_type))
                print(e)
                print(f"Class: {self.__str__()}\nMethod: {METHOD_NAME}\n")
                return pd.DataFrame(columns=OUTPUT_COLUMNS)
        else:
            print("Warning: One of the DataFrames is empty. It cannot be computed.")
            self.df_getpolarity = pd.DataFrame(columns=OUTPUT_COLUMNS)
            self.len_getpolarity = len(self.df_getpolarity)
