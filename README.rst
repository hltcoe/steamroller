------
SteamRoller |Logo|
------

SteamRoller is a framework for testing the performance of various machine learning models on different tasks in the broad area of "text classification".  It is designed to make it extremely easy to define new classification tasks, and new models, and drop them in to compare ther characteristics.  It discourages doing anything "special" for different tasks, models, or combinations thereof, to ensure the comparisons are fair and expose all the costs incurred by the different choices.

SteamRoller's user-facing functionality is reflected by four submodules:

1. tasks
2. models
3. metrics
4. plots

Under the hood, SteamRoller has three additional submodules:

1. tools
2. scons
3. ui

As explained below, changes to the code are usually unnecessary, as the most common conceptual classes (tasks and models) can be extended simply by editing the configuration file.

------
Getting started
------

SteamRoller and its dependencies can be installed with ``pip install steamroller --user``.  An empty directory can be initialized for performing experiments by executing ``steamroller init`` from therein.  This creates two files: *SConstruct*, and *steamroller_config.py*.  You can then run ``steamroller run`` to perform the predefined experiments, and ``steamroller serve`` to launch the results web server.  Most of SteamRoller's extensibility is through editing *steamroller_config.py*, while more advanced users may find it useful to edit *SConstruct*.

----
Using an HPC Grid
----

By default, *steamroller_config.py* will set ``GRID=False``, and experiments will run serially on the local machine.  If you are running on an HPC grid like Univa, Sun Grid Engine, or Torque, setting ``GRID=True`` instructs SteamRoller to run experiments via the *qsub* command.  Since the jobs are distributed across the grid, the invocation of SteamRoller will submit them and then *wait* until they have completed, polling the scheduler and printing the current number of running jobs.  If you interrupt the SteamRoller command in this state, *the grid jobs will continue to run*, so you can either allow them to do so (e.g. if the interruption was accidental), or manually kill the running jobs with a command like ``qdel -u USERNAME``.  The latter is particularly important if you want to change and rerun experiments, as otherwise you may have multiple jobs simultaneously building the same output file.

----
Viewing results
----

Once the experiments have finished, you will want to compare their performance.  

----
Defining a new task
----

----
Defining a new model
----

----
FAQ
----

.. |Logo|   image:: logo.png




The convention is that any file under `tasks/` represents a classification task, and should be a gzipped tar archive of Concrete Communications: see the examples in `custom.py.template`.  If you have your data in a text file with lines of `ID<tab>LABEL<tab>TEXT`, e.g.:

```
1235435    Spanish    Hola! Donde esta la biblioteca?
```

you can use the script `tools/convert_text_to_concrete.py` to create an appropriate tar archive of simple Communications:

```
python tools/convert_text_to_concrete.py -i YOUR_TEXT_FILE -o OUTPUT.tgz
```

### Instantiate a model

The convention for adding a new model is to place a script that performs training and classification under `models/`.  This script will be invoked twice for each experiment: the first time it will be passed four arguments: training, development, input, and output file names.  It should take these arguments and write a model to the output file.

The second time, it is also passed four arguments: model, test, input, and output file names.  It should apply the model to the test data, and write log-probabilities for each data point to the output file in format:

```ID TRUE_TAG LABEL1:LOGPROB1 LABEL2:LOGPROB2 ...```

Note that the train, dev, and test files are just gzipped lists of integers corresponding to lines in the input file: this is so we don't need to duplicate the data many times over.  See the model script `models/naive_bayes_wrapper.py` for an example of how they are used in combination with the input file.

### Modify custom.py

Aside from putting your data files and scripts in the right places, the only file you need to modify is `custom.py`.  Note that it isn't part of the actual git repository, it's meant to be where you define your own local experiments and customizations: `custom.py.template`, which *is* part of the repository, is a minimal example.  You will want to add entries to the `TASKS` or `MODELS` variables, as appropriate: see the comments in `custom.py.template` for more information.

### Measuring task performance

Each experiment produces a file with the probability distribution over labels for each test example, and to this one could apply a variety of evaluation metrics, and then plotted.  Currently, SteamRoller computes the f-score of the likeliest assignments, averaged evenly across the labels.  The scores are used to generate a whisker plot for each task, where the x-axis is the amount of data and y-axis is the score, so that models can be easily compared in terms of performance mean and variance.

### Measuring runtime performance

SteamRoller also records the CPU and maximum resident memory usage of each experimental step by wrapping the command in `time --verbose`.  These values are then used to generate whisker plots in the same fashion as the task performance, so the resource usage of the models can be compared.  The same approach is used to compare disk space used by serialized models.

## Advanced use

Since SCons is running each experiment by invoking user-defined scripts to train and apply models, it should have normal access to any resources (e.g. GPU) on the local machine.  Additionally, running SCons with the `-j N` option will allow up to `N` jobs to execute in parallel, which can significantly speed things up on a multi-core machine.  Work is under way on an SCons plugin that will allow experiments to be automatically mapped into a Grid Engine system for maximum throughput.

SCons is a very open-ended build system, and with Python being a dynamic language, it can be difficult to manage complexity.  So, you're encouraged to work in the patterns described above, adding experiments through the `custom.py` file.  If you run into a use-case that seems important but unsupported, feel free to contact me (tom@cs.jhu.edu).  If it represents a significant new class of experiments, maybe it warrants a new dedicated project!

## Questions

### Why is everything a script?

This is so we can easily run on an HPC grid.  Because of some design decisions inside SCons regarding build state and threading, it would be difficult to parallelize builders defined directly in terms of function calls.  Making every builder its own script also allows more flexibility in how models are implemented, particularly by non-Python coders.

### What about hyper-parameter search and the like?

There's nothing stopping you from generating lots of experiments over a range of hyper-parameter values ("grid search") and it would even be trivial to add visualization for this.  However, this adds another factor to the combinatorial space of experiments, and really the purpose of SteamRoller is *fair* comparisons: if a model requires a grid search to realize top performance, it should pay the price for this by optimizing in its training script.  This also saves us the complexity of thinking about dev splits and the like in SteamRoller itself.
