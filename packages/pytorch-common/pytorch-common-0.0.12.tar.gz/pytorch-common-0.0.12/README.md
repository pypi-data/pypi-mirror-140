# pytorch-common

A [Pypi module](https://pypi.org/project/pytorch-common/) with pytorch common tools like:

* **Callbacks** (keras style)
  * **Validation**: Model validation.
  * **ReduceLROnPlateau**:     
    * Reduce learning rate when a metric has stopped improving. 
    * Models often benefit from reducing the learning rate by a factor
      of 2-10 once learning stagnates. This scheduler reads a metrics
      quantity and if no improvement is seen for a 'patience' number
      of epochs, the learning rate is reduced.
  * **EarlyStop**:
    * Stop training when model has stopped improving a specified metric.
  * **SaveBestModel**: 
    * Save model weights to file while model validation metric improve.
  * **Logger**:
    * Logs context properties. 
    * In general is used to log performance metrics every n epochs.
  * **MetricsPlotter**:
    * Plot evaluation metrics. 
    * This graph is updated every n epochs during training process.
  * **Callback** and **OutputCallback**: 
    * Base classes.
  * **CallbackManager**:
    * Simplify callbacks support to fit custom models.
* **StratifiedKFoldCV**: 
  * Support parallel fold processing on CPU.
* **Mixins**
  * FiMixin
  * CommonMixin
* **Utils**
  * device management
  * stopwatch
  * data split
  * os
  * model
  * LoggerBuilder

