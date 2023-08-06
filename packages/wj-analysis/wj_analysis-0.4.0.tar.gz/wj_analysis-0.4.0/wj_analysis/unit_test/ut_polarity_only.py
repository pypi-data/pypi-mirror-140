#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  19 17:50:42 2021

@author: oscar
"""
import unittest

import pandas as pd

from wj_analysis.common.nlp_utils import Polarity

pd.options.mode.chained_assignment = None

sample_data = 1000

FOLDER = "/home/oscar/Labs/Data_polarity/"

df_com_fb = pd.read_csv(
    FOLDER + "Facebook/facebook_lib_facebook_comments.csv", low_memory=False
)
df_com_ig = pd.read_csv(
    FOLDER + "Instagram/instagram_lib_comment.csv", low_memory=False
)
df_com_tw = pd.read_csv(FOLDER + "Twitter/twitter_lib_tweetreply.csv", low_memory=False)

print("".center(60, "="))
print("ut_polarity_only_fb.py")
print("comments = " + str(sample_data * 3))
print("".center(60, "="))


class Test(unittest.TestCase):
    def setUp(self):
        """
        Variables to use in tests

        Returns
        -------
        None.

        """

        self.polarity = Polarity()
        self.df_com_s_fb = df_com_fb.sample(n=sample_data)
        self.df_com_s_ig = df_com_ig.sample(n=sample_data)
        self.df_com_s_tw = df_com_tw.sample(n=sample_data)
        self.df_empty = pd.DataFrame(columns=self.df_com_s_tw.columns)

    def test_data_normal(self):
        """
        This test with data ok

        Returns
        -------
        None.

        """
        print("".center(60, "="))
        print("TEST_DATA_NORMAL...")
        df_fb_normal = self.df_com_s_fb
        df_ig_normal = self.df_com_s_ig
        df_tw_normal = self.df_com_s_tw

        self.polarity.polarity_only(df_text=df_fb_normal, column_text="message")
        self.polarity.polarity_only(df_text=df_ig_normal, column_text="text")
        self.polarity.polarity_only(df_text=df_tw_normal, column_text="text")

        # valida dataframe no vacio
        self.assertGreater(len(df_fb_normal), 0)
        self.assertGreater(len(df_ig_normal), 0)
        self.assertGreater(len(df_ig_normal), 0)

        # valida una columna adicional con la polaridad
        self.assertEqual(len(df_fb_normal.columns), 17)
        self.assertEqual(len(df_ig_normal.columns), 11)
        self.assertEqual(len(df_tw_normal.columns), 45)

        print("".center(60, "-"))

    def test_data_empty(self):
        """
        This test with data empty

        Returns
        -------
        None.

        """
        print("".center(60, "="))
        print("TEST_DATA_EMPTY...")
        df_empty = self.df_empty

        self.polarity.polarity_only(df_text=df_empty, column_text="text")

        self.assertEqual(len(df_empty), 0)

        print("".center(60, "-"))

    @unittest.expectedFailure
    def test_wrong_column(self):
        """
        This test with data 20% null

        Returns
        -------
        None.

        """
        print("".center(60, "="))
        print("TEST_NAN_DATA...")
        df_fb_nc = self.df_com_s_fb
        df_ig_nc = self.df_com_s_ig
        df_tw_nc = self.df_com_s_tw

        self.polarity.polarity_only(df_text=df_fb_nc, column_text="sdf")
        self.polarity.polarity_only(df_text=df_ig_nc, column_text="fg")
        self.polarity.polarity_only(df_text=df_tw_nc, column_text="mesdfgdsage")

        # valida dataframe vacio por error en la columna
        self.assertGreater(len(df_fb_nc), 0)
        self.assertGreater(len(df_ig_nc), 0)
        self.assertGreater(len(df_tw_nc), 0)

        print("".center(60, "-"))


if __name__ == "__main__":
    unittest.main()
