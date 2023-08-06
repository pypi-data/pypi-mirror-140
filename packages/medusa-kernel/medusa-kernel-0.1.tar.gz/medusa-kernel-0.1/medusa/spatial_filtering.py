import numpy as np
from medusa import components
from numpy import linalg as nlinalg
from scipy import linalg as slinalg
import warnings


class LaplacianFilter(components.ProcessingMethod):
    """
    Class for fitting and applying Laplacian Filter to EEG Signals.
    A channel set from EEGChannelSet class must have been defined before calling
    LaplacianFilter class.
    """

    def __init__(self, channel_set, mode='auto'):
        super().__init__(apply_lp=['s_filtered'])
        """
        Constructor of class LaplacianFilter

        Parameters
        ----------
        channel_set: EEGChannelSet
            EEGChannelSet instance
        mode: str {'auto'|'custom'}
            Defines the behaviour of the filter:
                - auto: applies the laplacian filtering on the EEG signal,
                    subtracting the mean of  the n closest channels from each
                    EEG sample of each channel. The channels to be filtered can be set.
                - custom: applies the laplacian filtering on the EEG signal on
                    channels l_cha_to_filter, subtracting the mean of the
                    l_cha_laplace channels from each EEG sample .
        """

        # Parameters
        self.channel_set = channel_set
        self.l_cha = channel_set.l_cha
        self.n_cha = channel_set.n_cha
        self.mode = mode

        # Variables
        self.dist_matrix = None
        self.lp_filter = None
        self.idx_cha_to_filter = None

        # Check Channel Set is initialized
        if not channel_set.channels:
            raise Exception('Cannot compute the nearest neighbors if channel set '
                            'is not initialized!')

    def fit_lp(self, n_cha_lp=None, l_cha_to_filter=None, l_cha_laplace=None):
        """
        Fits the Laplacian Filter depending on the mode chosen

        Parameters
        ----------
        n_cha_lp: int
            Number of channels considered in the laplacian filter. Only used
            in mode auto.
        l_cha_to_filter: list
            List [N x 1] containing the labels of the channels to filter. Used in
            both filtering modes.
        l_cha_laplace: int
            List of lists [N x M] containing the labels of the channels to
            compute the laplace filter for channel in position Ni of
            l_cha_to_filter. Only used in mode custom
        """

        if self.mode == 'auto':
            # Check Errors
            if n_cha_lp is None:
                raise ValueError("[LaplacianFilter] In 'auto' mode is necessary to "
                                 "set the number og nearest channels to compute Laplacian"
                                 "filter in n_cha_lp")

            # Check if labels of channels to filter are set
            if l_cha_to_filter is None:
                self.dist_matrix = self.channel_set.compute_dist_matrix()
                self.lp_filter = np.empty((self.n_cha, n_cha_lp))
                for i in range(self.n_cha):
                    # Get the closest n channels
                    self.lp_filter[i, :] = np.argsort(self.dist_matrix[i, :])[1:n_cha_lp + 1]
                raise Warning("[LaplacianFilter] In 'auto' mode is available to "
                              "set Laplacian filtering channels  "
                              "in 'l_cha_to_filter'. Consider this if you do not want"
                              " to calculate the Laplacian filter for all channels.")
            else:
                self.dist_matrix = self.channel_set.compute_dist_matrix()
                self.lp_filter = np.empty((len(l_cha_to_filter), n_cha_lp))
                self.idx_cha_to_filter = np.empty(len(l_cha_to_filter))
                for i in range(len(l_cha_to_filter)):
                    # Get the indexes of channels to filter
                    self.idx_cha_to_filter[i] = self.l_cha.index(l_cha_to_filter[i])
                    # Get the closest n channels
                    self.lp_filter[i, :] = np.argsort(self.dist_matrix[self.idx_cha_to_filter[i].astype(int),
                                                      :])[1:n_cha_lp + 1]

        elif self.mode == 'custom':
            # Check Errors
            if l_cha_to_filter is None:
                raise ValueError("[LaplacianFilter] In 'custom' mode is necessary to "
                                 "set the labels of the channels to filter in"
                                 "'l_cha_to_filter'")

            if l_cha_laplace is None:
                raise ValueError("[LaplacianFilter] In 'custom' mode is necessary to "
                                 "set the labels of the channels to compute the "
                                 "Laplacian filter in 'l_cha_to_filter'.")

            self.lp_filter = np.empty((len(l_cha_to_filter), len(l_cha_laplace[0])))
            self.idx_cha_to_filter = np.empty(len(l_cha_to_filter))
            for i in range(len(l_cha_to_filter)):
                # Get the channel indexes
                self.idx_cha_to_filter[i] = self.l_cha.index(l_cha_to_filter[i])
                # Get the channel indexes for Laplacian filtering
                self.lp_filter[i, :] = [self.l_cha.index(x) for x in l_cha_laplace[i]]

    def apply_lp(self, signal):
        """
        Applies Laplacian filter to an EEG signal

        Parameters
        ----------
        signal: np.ndarray
            Array of EEG signal with shape [N_samples x N_channels]

        Returns
        -------
        s_filtered: np.ndarray
            - auto: Filtered EEG signal with shape [N_samples x N_channels]
                    if l_cha_to_filter not previously defined.
                    [N_samples x len(l_cha_to_filter)] otherwise.
            - custom: Filtered EEG signal with shape
                     [N_samples x len(l_cha_to_filter)]
        """
        s_filtered = None
        # Check dimensions
        if signal.shape[1] != len(self.l_cha):
            raise ValueError('Dimensions of s in axis 1 must match the number '
                             'of channels')
        # MODE AUTO
        if self.mode == 'auto':
            # Check if channels to filter are set:

            # All channels filtering
            if self.lp_filter.shape[1] == len(self.l_cha):
                s_filtered = signal - np.mean(signal[:, self.lp_filter.astype(int)], axis=2)

            # Chosen channels filtering
            else:
                s_filtered = signal[:, self.idx_cha_to_filter.astype(int)] - np.mean(
                    signal[:, self.lp_filter.astype(int)],
                    axis=2)

        # MODE CUSTOM
        elif self.mode == 'custom':
            s_filtered = signal[:, self.idx_cha_to_filter.astype(int)] - np.mean(signal[:, self.lp_filter.astype(int)],
                                                                                 axis=2)
        return s_filtered


def car(signal):
    """Implementation of the common average reference (CAR) spatial filter.

    This class applies a CAR filter over a signal with shape [samples x
    channels]. The CAR filtering substracts the averaged signal of all
    electrodes to every single one, following the expression below:

            X_car = X - (1/N)*sum(X,2),

    where X is the EEG signal with dimensions [samples x channels], N is the
    total number of channels, and sum(~,2) denotes the sum over the second
    dimension (i.e., over the channels, returning a [samples x 1] signal). In
    practice, this operation can be implemented as a matrix multiplication:

            X_car = (M * X')',

    where X is the original signal [samples x ch], and M is the spatial
    filter matrix, composed by:

                | 1-(1/N)   -1/N    -1/N  |
            M = | -1/N    1-(1/N)  -1/N   |
                | -1/N     -1/N   1-(1/N) |

    Parameters
    ----------
    signal: np.ndarray
        EEG raw signal with dimensions [samples x ch]. Note that the TRIGGER
        channel must be DELETED before calling this function. In other
        words, eeg_signal must not contain the TRIGGER channel, only the EEG
         channels.

    Returns
    -------
    signal: np.array
        Filtered signal

    """
    # Number of channels
    n_cha = signal.shape[1]
    if n_cha > 1:
        # Create the CAR spatial filter matrix
        m = np.ones([n_cha, n_cha]) * (-1 / float(n_cha))
        np.fill_diagonal(m, 1 - (1 / float(n_cha)))
        signal = np.dot(signal, m)
    return signal


class CSP(components.ProcessingMethod):
    """ The class CSP performs a Common Spatial Pattern filtering.

    Attributes
    ----------
    w: np.array
        Mixing matrix (spatial filters are stored in columns).
    eigenvalues:  np.array
        Eigenvalues of w.
    a: np.array
    De-mixing matrix (activation patterns are stored in columns).
    """

    def __init__(self):
        self.w = None  # Mixing matrix (spatial filters)
        self.eigenvalues = None  # Eigenvalues
        self.a = None  # De-mixing matrix

    def fit(self, x1, x2):
        """Common Spatial Patterns (CSP) in its most basic form.

        Parameters
        ----------
        x1: np.array
            Positive class (dimensions [channels x samples])
        x2: np.array
            Negative class (dimensions [channels x samples])
        """

        # Covariance matrices
        s1 = np.cov(x1)
        s2 = np.cov(x2)

        # Solve the eigenvalue problem
        l, w = slinalg.eig(s1, s1 + s2)
        eigenvalues = np.diag(l)
        a = slinalg.pinv2(w).T

        # Attribute storing
        self.w = w
        self.eigenvalues = eigenvalues
        self.a = a

    def apply(self, x):
        """ This method projects the input data X with the spatial filters W.
            :param x: Input data (dimensions [channels x samples]

            :return Filtered signal.
        """
        if self.w is None:
            raise Exception("CSP must be fitted first")
        return np.matmul(self.w.T, x)

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dict_data):
        csp = CSP()
        csp.w = dict_data['w']
        csp.eigenvalues = dict_data['eigenvalues']
        csp.a = dict_data['a']
        return csp


class CCA(components.ProcessingMethod):
    """
    The class CCA performs a Canonical Correlation Analysis filtering. First,
    function fit() sould be called to train the spatial filters. Then, spatial
    filters could be used to project testing data. After fit(), the following
    attributes are computed:

    Attributes
    ----------
    wx : {(channels, no_filters) ndarray}
        Mixing matrix for projecting the data, where spatial filters are stored
        in columns.
    wy : {(channels, no_filters) ndarray}
        Mixing matrix for projecting the reference, where spatial filters are
        stored in columns.
    r : {(channels, ) ndarray}
        Sample canonical correlations.
    """

    def __init__(self):
        self.wx = None
        self.wy = None
        self.r = None

    def fit(self, x, y):
        """
        Fits the CCA spatial filters given the two input matrices data and
        reference, storing relevant parameters.
        Parameters
        ----------
        x : {(samples, channels) ndarray}
            First input matrix, usually data with concatenated epochs.
        y : {(samples, channels) ndarray}
            Second input matrix, usually the data reference. The number of
            samples must match the samples of the data matrix. Repeat the
            reference if necessary before calling this function.
        """
        [self.wx, self.wy, self.r] = self.canoncorr(x, y)

    def project(self, data, filter_idx=(0), projection='wy'):
        """
        Projects the input data matrix using the given spatial filter. Note that
        the spatial filter will have dimensions
        Parameters
        ----------
        data : {(samples, channels) ndarray}
            Testing data matrix. The number of channels must be the same as the
            no. channels used to train.
        filter_idx : {int}, optional
            Indexes of the spatial filters to be used. Since filters are sorted by
            their importance in terms of correlation, the default filter (0) is
            the one that yields highest correlation.
        projection: {str}, optional
            Canonical coefficients to be used in projection. By default, the
            function uses Wy. Typically, if data is averaged, Wy must be used;
            otherwise, if data is not averaged and just concatenated, Wx must
            be used.
        Returns
        -------
        projected_data : {(samples, ) ndarray}
            Projected data along the selected spatial filter.
        """
        if projection.lower() == 'wy':
            return np.matmul(data, self.wy[:, filter_idx])
        elif projection.lower() == 'wx':
            return np.matmul(data, self.wx[:, filter_idx])
        else:
            raise Exception('[CCA] Unknown projection %s' % str(projection))

    @staticmethod
    def canoncorr(X, Y):
        """
        Computes the canonical correlation analysis (CCA) for the data matrices
        X (dimensions N-by-P1) and Y (dimensions N-by-P2). X and Y must have the
        same number of observations (rows) but can have different numbers of
        variables (cols). The j-th columns of A and B contain the canonial
        coefficients, i.e. the linear combination of variables making up the
        j-th canoncial variable for X and Y, respectively. If X or Y are less
        than full rank, canoncorr gives a warning and returns zeros in the rows
        of A or B corresponding to dependent columns of X or Y. Final dimension
        D is computed as D = min(rank_X, rank_Y).
        Notes
        ----------
        This method is adapted from the MATLAB function 'canoncorr'. Check
        that file in case of conflicts, doubts or additional information.
        Parameters
        ----------
        X : {(N, P1) ndarray}
            Input matrix with dimensions N-by-P1. Rows are observations and cols
            are variables.
        Y : {(N, P2) ndarray}
            Input matrix with dimensions N-by-P1. Rows are observations and cols
            are variables.
        Returns
        -------
        A : {(P1, D) ndarray}
            Sample canonical coefficients for the variables in X. The j-th
            column of A contains the linear combination of variables that makes
            up the j-th canonical variable for X. If X is less than full rank,
            A will have zeros in the rows corresponding to dependent cols of X.
        B : {(P2, D) ndarray}
            Sample canonical coefficients for the variables in Y. The j-th
            column of B contains the linear combination of variables that makes
            up the j-th canonical variable for Y. If Y is less than full rank,
            B will have zeros in the rows corresponding to dependent cols of Y.
        r : {(D,) ndarray}
            Sample canonical correlations. The j-th element of r is the
            correlation between the h-th columns of the canonical scores for
            the variables in X and Y.
        References
        -------
        [1] Krzanowski, W.J., Principles of Multivariate Analysis,
        Oxford University Press, Oxford, 1988.
        [2] Seber, G.A.F., Multivariate Observations, Wiley, New York, 1984.
        Example
        --------
        >>> import numpy as np
        >>> X = np.random.rand(10, 4)
        >>> Y = np.random.rand(10, 4)
        >>> A, B, r = canoncorr(X, Y)
        """
        # X dims
        if len(X.shape) == 1:
            n = X.shape[0]
            p1 = 1
            X = X.reshape(n, 1)
        else:
            [n, p1] = X.shape

        # Check the input size
        if Y.shape[0] != n:
            raise ValueError('[canoncorr] Input size mismatch')
        elif n == 1:
            raise ValueError('[canoncorr] Not enough data')

        # Y dims
        if len(Y.shape) == 1:
            p2 = 1
            Y = Y.reshape(n, 1)
        else:
            p2 = Y.shape[1]

        # Center the variables
        X = X - np.mean(X, 0)
        Y = Y - np.mean(Y, 0)

        # Factor the inputs and find a full rank set of columns if necessary
        [Q1, T11, perm1] = slinalg.qr(X, mode='economic', pivoting=True)
        rankX = nlinalg.matrix_rank(T11)
        if rankX == 0:
            raise ValueError('[canoncorr] Rank of X is 0. Invalid Data')
        elif rankX < p1:
            warnings.warn('[canoncorr] Data X is not full rank')
            Q1 = Q1[:, 0:rankX]
            T11 = T11[0:rankX, 0:rankX]
        [Q2, T22, perm2] = slinalg.qr(Y, mode='economic', pivoting=True)
        rankY = nlinalg.matrix_rank(T22)
        if rankY == 0:
            raise ValueError('[canoncorr] Rank of Y is 0. Invalid Data')
        elif rankY < p2:
            warnings.warn('[canoncorr] Data Y is not full rank')
            Q2 = Q2[:, 0:rankY]
            T22 = T22[0:rankY, 0:rankY]

        # Compute canonical coefficients and canonical correlations. For
        # rankX > rank Y, the economy-size version ignores the extra columns
        # in L and rows in D. For rankX < rankY, need to ignore extra columns
        # in M and explicitly. Normalize A and B to give U and V unit variance
        d = np.min([rankX, rankY])
        [L, D, M] = nlinalg.svd(np.matmul(Q1.T, Q2))
        M = M.T
        A = nlinalg.lstsq(T11, L[:, 0:d], rcond=None)[0] * np.sqrt(n - 1)
        B = nlinalg.lstsq(T22, M[:, 0:d], rcond=None)[0] * np.sqrt(n - 1)
        r = D[0:d]
        r[r < 0] = 0  # remove roundoff errors
        r[r > 1] = 1

        # Put coefficients back to their full size and their correct order
        A = np.concatenate((A, np.zeros((p1 - rankX, d))), axis=0)
        A = A[np.argsort(perm1), :]
        B = np.concatenate((B, np.zeros((p2 - rankY, d))), axis=0)
        B = B[np.argsort(perm2), :]

        return A, B, r

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(dict_data):
        cca = CCA()
        cca.wx = dict_data['wx']
        cca.wy = dict_data['wy']
        cca.r = dict_data['r']
        return cca
