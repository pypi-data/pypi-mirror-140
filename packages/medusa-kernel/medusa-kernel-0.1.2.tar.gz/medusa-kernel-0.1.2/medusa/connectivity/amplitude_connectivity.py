import scipy.signal as signal
import scipy.stats as stats
import scipy .special as special
import numpy as np
from medusa import signal_orthogonalization as orthogonalizate
from medusa.hilbert import hilbert
from medusa import pearson_corr_matrix as corr
import os
import time
from numba import jit, objmode


def __aec_gpu(data):
    """
    This function calculates the amplitude envelope correlation using GPU
    
    Parameters
    ----------
    data : numpy 2D matrix
        MEEG Signal. SamplesXChannel.
        
    Returns
    -------
    aec : numpy 2D matrix
        Array of size ChannelsXChannels containing aec values.
        
    """
    import tensorflow as tf
    import tensorflow_probability as tfp
    # ERROR CHECK
    if (type(data) != np.ndarray):
        raise ValueError("Parameter data must be of type numpy.ndarray")
    
    # VARIABLE INITIALIZATION
    # aec = tf.zeros((data.shape[0],data.shape[0]))
    # aec[:] = np.nan

    #  AEC CALCULATION
    hilb = hilbert(data)
    envelope = tf.math.abs(hilb) 
    env = tf.math.log(tf.math.square(envelope))
    aec = tfp.stats.correlation(env)
        
    return aec


def __aec_cpu(data):
    """
    This function calculates the amplitude envelope correlation using CPU
    
    Parameters
    ----------
    data : numpy 2D matrix
        MEEG Signal. SamplesXChannel.
        
    Returns
    -------
    aec : numpy 2D matrix
        Array of size ChannelsXChannels containing aec values.
        
    """
    # ERROR CHECK
    if (type(data) != np.ndarray):
        raise ValueError("Parameter data must be of type numpy.ndarray")
    
    #  VARIABLE INITIALIZATION
    aec = np.empty((len(data[0]),len(data[0])))
    aec[:] = np.nan

    # AEC CALCULATION
    hilb = hilbert(np.transpose(data))
    envelope = abs(hilb) 
    env = np.log(envelope**2)
    aec = corr.pearson_corr_matrix(np.transpose(env), np.transpose(env)) 
        
    return aec


def __aec_ort_gpu(data):
    """
    This function calculates the orthogonalized version of the amplitude 
    envelope correlation using GPU. This orthogonalized version minimizes the 
    spurious connectivity caused by common source
    
    Parameters
    ----------
    data : numpy 2D matrix
        MEEG Signal. SamplesXChannel.
        
    Returns
    -------
    aec : numpy 2D matrix
        Array of size ChannelsXChannels containing orthogonalized aec values.
        
    """
    import tensorflow as tf
    import tensorflow_probability as tfp
    # Error check
    if (type(data) != np.ndarray):
        raise ValueError("Parameter data must be of type numpy.ndarray")
    
    # Variable inicialization
    num_chan = len(data[0])    
    aec = np.empty((num_chan,num_chan))
    aec[:] = np.nan
    
    # AEC Ort Calculation (CPU orthogonalization is much faster than GPU one)
    signal_ort = orthogonalizate.signal_orthogonalization_cpu(data, data)

    signal_ort_2 = tf.transpose(tf.reshape(tf.transpose(signal_ort),
                                           (num_chan*num_chan,
                                            len(signal_ort))))
    hilb_1 = hilbert(signal_ort_2)
    envelope_1 = tf.math.abs(hilb_1) 
    env = tf.math.log(tf.math.square(envelope_1) )     
    aec_tmp = tfp.stats.correlation(env)
    aec_tmp2 = tf.transpose(
        tf.reshape(
            tf.transpose(aec_tmp),
            (tf.cast(aec_tmp.shape[0]*aec_tmp.shape[0]/num_chan, tf.int32), -1)
        )
    )
    idx = tf.cast(tf.linspace(0, len(aec_tmp2[0]) -1, num_chan), tf.int32)
    aec = tf.gather(aec_tmp2, idx, axis=1).numpy()

    # # Another way of calculating the AEC
    # for n_chan in range(0,num_chan):
    #     hilb_1 = hilbert(np.asarray(signal_ort[:,:,n_chan]))
    #     envelope_1 = tf.math.abs(hilb_1) 
    #     env = tf.math.log(tf.math.square(envelope_1) )
    #     aec[:,n_chan] = tf.transpose(tf.slice(tfp.stats.correlation(env),[0,n_chan],[len(data[0]),1]))
        
    # Orthogonalize A regarding B is not the same as orthogonalize B regarding 
    # A, so we average lower and upper triangular matrices to construct the 
    # symmetric matrix required for Orthogonalized AEC 

    aec_upper = tf.linalg.band_part(aec, 0, -1)
    aec_lower = tf.transpose(tf.linalg.band_part(aec, -1, 0))
    aec_ort = tf.math.divide(tf.math.add(aec_upper,aec_lower),2);
    aux = tf.linalg.band_part(aec_ort, 0, -1) - tf.linalg.band_part(aec_ort, 0, 0)
    aec_ort = tf.math.abs(tf.math.add(aux,tf.transpose(aec_ort)))  
        
    return aec_ort


def __aec_ort_cpu(data, verbose=False):
    """
    This function calculates the orthogonalized version of the amplitude 
    envelope correlation using CPU. This orthogonalized version minimizes the 
    spurious connectivity caused by common source
    
    Parameters
    ----------
    data : numpy 2D matrix
        MEEG Signal. SamplesXChannel.
        
    Returns
    -------
    aec : numpy 2D matrix
        Array of size ChannelsXChannels containing orthogonalized aec values.
        
    """
    # Error check
    if (type(data) != np.ndarray):
        raise ValueError("Parameter data must be of type numpy.ndarray")

    # Init
    n_cha = len(data[0])
    
    # AEC Ort Calculation
    t_ort = time.time()
    signal_ort = orthogonalizate.signal_orthogonalization_cpu(data, data)
    t_ort = time.time() - t_ort

    # Can't be calculated without a loop because for each channel you need 
    # different signals (the signals orthogonalized regarding that channel)
    t_aec_loop = time.time()
    # Init
    aec = np.empty((n_cha, n_cha))
    aec[:] = np.nan
    # Can't be calculated without a loop because for each channel you need
    # different signals (the signals orthogonalized regarding that channel)
    for cha in range(n_cha):
        hilb = hilbert(signal_ort[:, :, cha].T)
        env = np.log(np.square(np.abs(hilb)))
        aec[:, cha] = np.corrcoef(env)[:, cha]
    t_aec_loop = time.time() - t_aec_loop

    # Orthogonalize A regarding B is not the same as orthogonalize B regarding
    # A, so we average lower and upper triangular matrices to construct the 
    # symmetric matrix required for Orthogonalized AEC
    t_adj = time.time()
    aec_upper = np.triu(np.squeeze(aec))
    aec_lower = np.transpose(np.tril(np.squeeze(aec)))
    aec_ort = (aec_upper + aec_lower) / 2
    aec_ort = abs(np.triu(aec_ort, 1) + np.transpose(aec_ort))
    t_adj = time.time() - t_adj

    # Timings report
    if verbose:
        print()
        print('------- AEC performance report --------')
        print(">> Orthogonalization - %fs" % t_ort)
        print(">> AEC loop - %fs" % t_aec_loop)
        print(">> Average Adjacency matrices - %fs" % t_adj)
        print()

    return aec_ort


def aec(data, ort=True):
    """
    Calculates the amplitude envelope correlation.

    Parameters
    ----------
    data : numpy 2D matrix
        Time series. SamplesXChannels.
    ort : bool
        Orthogonalize or not the signal: removes volume conduction effects.
        Default True
        
    Returns
    -------
    aec : numpy 2D matrix
        Array of size ChannelsXChannels containing aec values.    

    """
    from medusa import tensorflow_integration
    #  ERROR CHECK
    if not np.issubdtype(data.dtype, np.number):
        raise ValueError('data matrix contains non-numeric values') 

    if not ort:
        if tensorflow_integration.check_tf_config(autoconfig=True):
            aec = __aec_gpu(data)
        else:
            aec = __aec_cpu(data)

    else:
        if tensorflow_integration.check_tf_config(autoconfig=True):
            aec = __aec_ort_gpu(data)
        else:
            aec = __aec_ort_cpu(data)

    return aec


def matrix_correlation(data, mode='Spearman', trunc=False):
    """
    Calculates the amplitude envelope correlation.

    Parameters
    ----------
    data : numpy 2D matrix
        Time series. SamplesXChannels.
    mode : string
        Pearson or Spearman. Default Spearman. NOTE: Pearson requires normally
        distributed data
    trunc : bool
        If True, non-significant correlation values will be considered 0.
        Default False

    Returns
    -------
    correlation : numpy 2D matrix
        Array of size ChannelsXChannels containing aec values.

    """
    #  ERROR CHECK
    if not np.issubdtype(data.dtype, np.number):
        raise ValueError('data matrix contains non-numeric values')
    if not isinstance(trunc, bool):
        raise ValueError('trunc must be a boolean variable')

    if mode == 'Spearman':
        n = data.shape[0]
        corr = np.corrcoef(data, rowvar=False)
        ab = n / 2 - 1
        p_val = 2 * special.btdtr(ab, ab, 0.5 * (1 - abs(np.float64(corr))))

        # corr, p_val = stats.spearmanr(data)
    elif mode == 'Pearson':
        corr = np.zeros((data.shape[1], data.shape[1]))
        p_val = np.zeros((data.shape[1], data.shape[1]))
        for i in range(data.shape[1]):
            for j in range(data.shape[1]):
                corr[i, j], p_val[i, j] = stats.pearsonr(data[:, i], data[:, j])
    else:
        raise ValueError('Unknown correlation mode')

    if trunc:
        corr[p_val > 0.05] = 0

    return corr, p_val


if __name__ == "__main__":
    import scipy.io
    import time
    mat = scipy.io.loadmat('D:/OneDrive - gib.tel.uva.es/Bases de Datos/'
                           'Japon/MEG/n3_Control_Filtrados_Adaptados/'
                           'Adaptados/0001_Control.mat')
    vector = np.array(mat["data"])[0:50, :]
    # salida = aec(vector, 'CPU', True)

    t0 = time.time()
    salida1, pv1 = matrix_correlation(vector, mode='Pearson', trunc=False)
    t1 = time.time()
    salida2, pv2 = matrix_correlation(vector, mode='Spearman', trunc=False)
    t2 = time.time()
    print('Tmp Pear: ', t1 - t0)
    print('Tmp Spear: ', t2 - t1)
    aa = 0
