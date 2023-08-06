from sklearn.linear_model import LogisticRegression as LogR, LinearRegression as LinR
from pyspark.ml.classification import LogisticRegression as SparkLogR
from pyspark.ml.regression import LinearRegression as SparkLinR


class PredictorBase:
	def __init__(
			self, model, x_columns=None, y_column=None, normalize=False
	):
		"""
		:type model: LogR or LinR or SparkLogR or SparkLinR
		:type x_columns: str or list[str] or tuple or set or NoneType
		:type y_column: str or list[str] or tuple or set or NoneType
		"""
		self._untrained_model = None
		self._trained_model = None
		self._x_columns = None
		self._y_column = None
		self._normalize = normalize

		if x_columns is not None:
			self.x_columns = x_columns

		if y_column is not None:
			self.y_column = y_column

		self.untrained_model = model

	@property
	def x_columns(self):
		"""
		:rtype: list[str]
		"""
		return self._x_columns

	@x_columns.setter
	def x_columns(self, x_columns):
		"""
		:type x_columns: str or list[str] or tuple or set
		"""
		if self._x_columns is not None:
			raise RuntimeError('x_columns has already been set!')

		if isinstance(x_columns, str):
			x_columns = [x_columns]
		elif isinstance(x_columns, (tuple, set)):
			x_columns = list(x_columns)
		elif not isinstance(x_columns, list):
			raise TypeError(f'x_columns of type {type(x_columns)} is not supported!')

		if not all([isinstance(col, str) for col in x_columns]):
			raise TypeError(f'x_columns should be strings!')

		self._x_columns = x_columns

	@property
	def y_column(self):
		"""
		:rtype: str
		"""
		return self._y_column

	@y_column.setter
	def y_column(self, y_column):
		"""
		:type y_column: str or list[str] or tuple or set
		"""
		if self._y_column is not None:
			raise RuntimeError('y_column has already been set!')

		if isinstance(y_column, (set, tuple, list)):
			if len(y_column) > 1:
				raise ValueError('Too many values for y_column!')
			y_column = y_column[0]

		if not isinstance(y_column, str):
			raise TypeError(f'y_column of type {type(y_column)} is not supported!')

		self._y_column = y_column

	@property
	def untrained_model(self):
		"""
		:rtype:
		"""
		return self._untrained_model

	@untrained_model.setter
	def untrained_model(self, untrained_model):
		"""
		:type untrained_model:
		"""
		if self._untrained_model is not None:
			raise RuntimeError('untrained model has already been set!')

	@property
	def trained_model(self):
		"""
		:rtype:
		"""
		return self._trained_model
