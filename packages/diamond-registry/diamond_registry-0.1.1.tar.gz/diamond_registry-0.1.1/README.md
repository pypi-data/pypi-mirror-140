# Data Revenue Diamonds Code Challenge

Congratulations on making it to the code challenge! 

In this stage you will implement a small project. This document contains all the details - please read it all before starting.

In case of any questions, don't hesitate to write an email to hiring@datarevenue.com.

## Story

Your client is a diamond tycoon. It's a company which owns a network of jewelry stores and needs a system to track the diamonds they sell, and to estimate prices of new diamonds.

## Part I: Diamond registry Python package

Your task is to implement a `diamond_registry` Python package. The package should allow for adding, storing and retrieving information about diamonds.

The package will be used only from within other Python scripts, so you don't need to implement any command-line or network interface.

### Specification

- Each diamond has the following attributes:
  - `id` - unique identifier (integer)
  - `price` - price in US dollars (only whole dollars, no cents)
  - `carat` - weight of the diamond in grams
  - `cut` - quality of the cut (Fair, Good, Very Good, Premium, Ideal)
  - `color` - diamond colour, from J (worst) to D (best)
  - `clarity` - a measurement of how clear the diamond is (I1 (worst), SI2, SI1, VS2, VS1, VVS2, VVS1, IF (best))
  - `x` - length in mm
  - `y` - width in mm
  - `z` - depth in mm
  - `depth` - total depth percentage = z / mean(x, y) = 2 * z / (x + y)
  - `table` - width of top of diamond relative to the widest point
- Each diamond has 0 or more certificates. Available certificates are: GIA, AGS, GCAL, IGI, EGL.
- Each diamond is assigned to one jewelry store.
  - Each store has the following attributes:
    - `city`
    - `country`
  - There is no more than one store in a given city.
  - The client indicated that in the future the system might be extended to keep track of more details of each store, including hired staff.

### Requirements

The package should provide Python functions with the following functionalities:
- configure the system
- add a new diamond
- list diamonds
  - without any filters
  - assigned to a given store
  - having certain certificates
  - any combination of the above filters
- batch-import items from an external file

Details follow.

#### Public functions
The package should provide public functions listed below.

You can find stubs of all the required functions in `diamond_registry_stubs.pyi` file. Please stick to the provided function signatures, as your submission will be automatically tested. You are not required to use the stub file in your package.

Required public functions:

- `diamond_registry.configure`
  - If the data is stored in a database (see `Data storage` section below):
    - should allow setting database connection details,
    - should create needed tables if they don't exist.

- `diamond_registry.add_diamond`
  - Adds a new diamond to the registry.  
  - If `id` is not given, it should be automatically assigned.
  - If `id` is given but a diamond with this id already exists in the system, a `ValueError` should be raised
  - Should return id of the newly added diamond.

- `diamond_registry.get_diamonds`
  - Returns a list of diamonds matching **all** the given filters.
  - If no items match the filters, empty list should be returned.
  - Objects in the returned list should support getting `id` key, i.e. doing this: `get_diamonds()[0]["id"]` should give the id of the first returned diamond.
  - Order in which diamonds are returned does not matter.

- `diamond_registry.delete_all`
  - Erases all the data from the system.

- `diamond_registry.batch_import`
  - Reads a CSV file from a remote URL and adds all diamonds listed in it to the system.
  - You can assume that this function will be called when the system is empty, i.e. after calling `delete_all`.
  - See below for details.

Public functions must be available at a package level. I.e., they will be called like this:
```python
import diamond_registry
diamond_registry.add_diamond(...)
```

#### Batch import
The batch-import functionality should import data from a file stored at a publicly accessible web URL.
The file will be in CSV format. It will have a following structure:
```csv
"id","carat","cut","color","clarity","depth","table","price","x","y","z","certificates","store_city","store_country"
1,0.23,"Ideal","E","SI2",61.5,55.0,326,3.95,3.98,2.43,"IGI,GCAL","Palermo","Italy"
2,0.21,"Premium","E","SI1",59.8,61.0,326,3.89,3.84,2.31,"","Vilnius","Lithuania"
```

See Data section below.

#### Data storage

The system should store the data in an external, persisted, relational database: either MySQL or PostgreSQL. (If you really want to use a different engine, please contact us first.) Connection to the database should be configurable via `configure` method.

Provisioning a database server is out of scope of this challenge - see the `Ready-to-use database server` section below. In your submission please include the information which database engine your application requires.

If you have troubles implementing database support, you can also store the data in a different way - in memory (so that the data is lost when the process ends) or in local files. Keep in mind though that an implementation supporting a database will give you more points.

### What will be judged
Your submission should contain a proper Python package. We will judge if the package is properly organised, documented and pip (or conda)-installable.

We will run a suite of tests on your code to assert that it works correctly, according to the requirements. Some tests will be basic, other will be more tricky, testing the edge cases. The more tests your code passes, the better.

We will judge the code quality. Your code will be reviewed by a human (possibly more than one). Most of all, the code should be clean and understandable; we will also judge all the good practices that we are aware of.

You can implement the package however you like, but object-oriented implementation gives you extra points.


## Part II: Machine learning

Your task is to create a machine learning model that can estimate a price of a new diamond, and report about this model to the client.

We realise that data exploration and model selection process can be messy. You don't have to include it in your submission (but you certainly can).

You should, however, include the whole pipeline of preprocessing the data, training a final model and evaluating it. It can be done in a Jupyter notebook if you wish (please include cell outputs in your submission.) The script/notebook used for training and evaluating the final model should be runnable.

Please prepare a final report that you will present to the client's management board. Remember that these people are not programmers, nor data scientists. Present the information that you think is relevant for them. The report can be in any form - PDF, Jupyter notebook, Google Docs file, etc. Please include the report in your submission. You will be asked to present it during our next call, where we will act as the client.

### What will be judged

We will judge the code quality and whether you follow best practices of machine learning. It would be great if a model had good performance, but this is not of our main interest.


## Data

The data is available here:
  - full data: https://datarevenue-public.s3.eu-central-1.amazonaws.com/code-challenge/diamonds/dr_diamonds_challenge.csv
  - short data: https://datarevenue-public.s3.eu-central-1.amazonaws.com/code-challenge/diamonds/dr_diamonds_challenge_head.csv

Information about diamond certificates, as well as store details, is random - it won't be useful for your model.


## Other details

In this repository you can't push (or merge) to `master` branch. Please create a `dev` branch and push your changes to it. You can create other branches of course, and commit/push as often as you want. When you are done, please create a Merge Request from `dev` into `master` and let us know about it by sending an email to hiring@datarevenue.com. We will review your submission then.

Use Python version not lower than 3.6.

### Ready-to-use database server

We have provided a docker-compose file that spins up two database servers on your computer (MySQL and PostgreSQL). Of course you don't have to use it - you can configure a DB server on your own.

Please install Docker Engine and Docker Compose on your computer. On Windows and Mac, they are included in [Docker Desktop](https://docs.docker.com/desktop/) installation. On Linux, you must install them separately; see [Docker Engine instructions](https://docs.docker.com/engine/install/) and [Docker Compose instructions](https://docs.docker.com/compose/install/).

Once you have docker-compose installed, run the `docker-compose.yml` from this repository in your Docker Desktop. Alternatively, open a terminal window, `cd` to the root folder of this repository and run the following command:

    docker-compose up

You should now have two DB servers running on your system. Additionally, there's a web interface available at http://localhost:8080 which you can use to inspect your database.

Please find the details below:

|                  | MySQL          | PostgreSQL     |
|------------------|----------------|----------------|
| host (local)*    | localhost      | localhost      |
| host (Adminer)** | mysql          | postgres       |
| port             | 3306           | 5432           |
| username         | diamonds_user  | diamonds_user  |
| password         | myuserpassword | myuserpassword |
| database name    | diamonds       | diamonds       |

*host(local) - when connecting from a local process, like Python  
**host(Adminer) - when connecting from a web interface at http://localhost:8080

## Good luck!
