# Design Doc


The goal of this project is to basically build 'distributed Luigi'. Building on the concepts of Luigi but allow for two main differences:

1. The Scheduler has more redundancy. Currently the state of the scheduler is stored in a pickle file written to disk. You can save task history to a DB, but it'd be great to have multiples.
2. Workers are basically 'executors'. They get a task and some arguments and execute
3. Maintain the ease of luigi's development process with the local scheduler. I want be like `cli run task_name parameter_1=1 paramater=2` and it runs it locally w/ cached data.


Other features:
- A task has an optional 'rollback' functionality. That is, if it fails it will attempt to rollback and retry.
- Tasks are basically wrappers around another computational engine. The business logic is minimal.
- There is some kind of 'type checking' on inputs built in. Probably leverage things like Pandera etc.



## Thoughts

Main state is tracked in a database utilized by sqlalchemy.

Worker tasks are distributed across a tool like redis or celery. I'm thinking redis at least initially because it'll be easier to set up/share state.



## Tasks

Task are a 'unit of work'. That is they're intended to do one thing, most likely call an external service or run some specific python code.

One difference from Luigi is that 'configuration' and 'parameters' are broken out into separate arguments:
- Configuration: Is the application runtime config, is this running in prod or locally? Where should files be saved etc
- Parameters: Are specific business logic parameters.



## Scheduler

No clue atm. It'll execute the dag by distributing the tasks to a set of workers, either through push or maybe by pull. Something something consensus algorithm.

One interesting distributed DB might be [litestream](https://litestream.io/) a distributed SQLite tool.
