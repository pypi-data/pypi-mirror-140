# Beta modal regression with measurement error

## Import data

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import pybetareg as pyb

    ## Beta Modal Regression in Python.

    df1 = pd.read_csv("data.csv")
    df1.head()

    ##           Y      Wbar    SigmaW   Z1
    ## 0  0.186046 -2.289838  1.732051  0.0
    ## 1  0.391666 -0.535476  1.732051  0.0
    ## 2  0.883178  2.071954  1.732051  1.0
    ## 3  0.727209 -0.578447  1.732051  0.0
    ## 4  0.269854 -0.926259  1.732051  0.0

    y = df1['Y'].to_numpy()
    w = df1['Wbar'].to_numpy()
    z = df1['Z1'].to_numpy()
    z = np.column_stack([np.ones(z.shape[0]),z])
    sigmaw = df1['SigmaW'].to_numpy()

## Fit model

    model2 = pyb.reg_measurement_error(y=y,w=w,z=z,
                                       sigmaw=sigmaw,
                                       initial=[10,1,1,1],
                                       CUDA = True,
                                       column_names = ['b1','b0','b2'])
    model2fit = model2.fit()
    model2fit.summary()

    ## -----------------------Model fitting completes------------------------
    ## Success:True
    ## Optimization terminated successfully.
    ## """
    ##                   Beta Modal Regression Results With                  
    ##                      Measurement Error Adjustment                     
    ## ======================================================================
    ##                 coef   std err         z     P>|z|    [0.025    0.975]
    ## ----------------------------------------------------------------------
    ## m            12.3424     3.791     3.256     0.001     4.913    19.772
    ## b1            0.9733     0.453     2.150     0.032     0.086     1.860
    ## b0            1.0646     0.436     2.444     0.015     0.211     1.918
    ## b2            0.9807     0.442     2.217     0.027     0.114     1.847
    ## ======================================================================
    ## """

## Hotelling's *T*<sup>2</sup> statistic and parametric bootstrap *p*-value.

Use `hotelling_p(50)` function to calculate Hotelling's *T*<sup>2</sup>
statistic and parametric bootstrap *p*-value across 50 iterations.

    model2.hotelling_p(50)

    ## Hotelling's T^2 statistic and parametric bootstrap p-value.      
    ## ======================================================================
    ## Hotelling's T^2 statistic: 0.5063
    ## parametric bootstrap p-value: 0.7000
    ## ======================================================================

# Beta modal regression without measurement error

## Import data

    df2 = pd.read_csv("data2.csv")
    df2.head()

    ##           Y   X0        X1   X2
    ## 0  0.133439  1.0 -2.223525  0.0
    ## 1  0.315374  1.0 -1.415762  0.0
    ## 2  0.845555  1.0  1.218485  1.0
    ## 3  0.977328  1.0  1.690799  1.0
    ## 4  0.811748  1.0  0.076872  0.0

## Fit model

    x = df2[['X0','X1','X2']]
    y = df2['Y']
    model1 = pyb.reg(x=x, y=y, initial = [10,1,1,1])
    model1fit = model1.fit()
    model1fit.summary()

    ## Link function:logit
    ## Columns names are not given.
    ## Success:True
    ## Optimization terminated successfully.
    ## """
    ##                     Beta Modal Regression Results                     
    ## ======================================================================
    ##                 coef   std err         z     P>|z|    [0.025    0.975]
    ## ----------------------------------------------------------------------
    ## m            11.1426     1.253     8.891     0.000     8.686    13.599
    ## beta0         0.9453     0.113     8.373     0.000     0.724     1.167
    ## beta1         0.8837     0.084    10.571     0.000     0.720     1.048
    ## beta2         1.1198     0.182     6.158     0.000     0.763     1.476
    ## ======================================================================
    """
