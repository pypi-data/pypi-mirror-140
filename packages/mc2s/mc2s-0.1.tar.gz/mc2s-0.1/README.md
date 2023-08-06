# MC2S

MC2S provides a script to apply MCR-ALS and projection using least squares regression based on [CARS data](https://gitlab.xlim.fr/datacart/cars-data) package.

## Datasets
Datasets can be provided on request at damien.boildieu@xlim.fr

## Usage
To launch the main script :
```
carsdata
```
You can also provide directly the configuration file with :
```
carsdata -j path/to/configuration/file.json
```

Configuration files are in JSon format, examples of configuration are available in the ```configs``` folder.
Configuration attributes are the same as objects constructors in the source code. Hence, ```mc2.json``` contains:
```json
{
  "data" : ["Path/to/file"],
  "analyzer" : 
  {
      "MCR" :
      {
        "output_dim" : 5,
        "guesser" :
        {
          "Simplisma" :
          {
            "simp_err" : 5
          }
        },
        "c_regr" : 
        {
          "NNLS" : {}
        },
        "c_constr" : 
        {
          "ChanVeseConstraint":
          {
          "nu": 0,
          "lambda1": 1,
          "lambda2": 1,
          "mu": 0.35
          },
          "NormConstraint" :
          {
            "axis" : 1
          }
        },
        "st_regr" : 
        {
          "NNLS" : {}
        },
        "st_constr" : {}
      }
  },
  "vspan" : [
    {
      "begin" : 3180,
      "end" : 3200,
      "color" : "cyan"
    },
    {
      "begin" : 3046,
      "end" : 3066,
      "color" : "green"
    },
    {
      "begin" : 2997,
      "end" : 3017,
      "color" : "red"
    },
    {
      "begin" : 2910,
      "end" : 2930,
      "color" : "green"
    },
    {
      "begin" : 2834,
      "end" : 2854,
      "color" : "red"
    }
  ],
  "spectra_colors" : [
    "darkmagenta",
    "mediumvioletred",
    "navy",
    "teal",
    "saddlebrown"
  ]
}
```