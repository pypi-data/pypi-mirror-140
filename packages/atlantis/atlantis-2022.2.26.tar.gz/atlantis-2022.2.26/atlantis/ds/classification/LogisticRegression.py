from pyspark.sql import DataFrame as SparkDF
from pandas import DataFrame as PandasDF, Series as PandasSeries
from sklearn.linear_model import LogisticRegression as SkleanLR
from pyspark.ml.classification import LogisticRegression as SparkLR


class LogisticRegression:
	def __init__(self, x_columns, y_column, normalize=False):
		self._x_columns = x_columns
		self._y_column = y_column
		self._normalize = normalize
		self._untrained_model = None
		self._trained_model = None

	def fit(self, data):
		"""
		:type data: SparkDF or PandasDF
		:rtype: LogisticRegression
		"""



