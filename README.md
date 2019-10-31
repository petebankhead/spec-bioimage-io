# Bioimiage.io Configuration Specification

The model zoo specification contains configuration definitions for the following categories:
- `Transformation`: configuration of a tensor to tensor transformation, that can be used for pre-processing operations (like normalization), post-processing, etc.
- `Model`: configuration of a trainable (deep-learning) model.
- `Reader`: configuration of a data-source + how to read from it.
- `Sampler`: configuration of a sampling procedure given a `Reader.`

The configurations are represented by a yaml file.


## Common keys

Each configuration must contain the following keys:
`name`, `description`, `cite`, `authors`, `documentation`, `tags` `format_version`, `language`, `framework`,`source`, `kwargs`.
[//]: # Do we have any optional config keys?

### `name`
Name of the transformation. This name should equal the name of any existing, logically equivalent object of the same category in another framework.

###  `description`
A string containing a brief description. 

### `cite`
A citation entry or list of citation entries.
Each entry contains of a mandatory `text` field and either one or both of `doi` and `url`.

### `authors`
A list of author strings. 
A string can be seperated by `;` in order to identify multiple handles per author.

### `documentation`
Relative path to file with additional documentation in markdown.

### `tags`
A list of tags.

### `format_version`
Version of this bioimage.io configuration specification.

### `language`

Programming language of the model definition. For now, we support `python` and `java`.
[//]: # `javascript`?

###  framework

The deep learning framework for which this object has been implemented. For now, we support `pytorch` and `tensorflow`.
Can be `null` if the implementation is not framework specific.

### `source`

Language and framework specific implementation. This can either point to a local implementation:
`<relative path to file>:<identifier of implementation within the source file>`

or the implementation in an available dependency:
<root-dependency>.<sub-dependency>.<identifier>

For example:
- ./my_function:MyImplementation
- core_library.some_module.some_function
[//]: # TODO java: <path-to-jar>:ClassName ?

### `kwargs`
Keyword arguments for the implementation specified by [`source`](#source).

[//]: # Do we want any positional arguments ? mandatory or optional?


## Transformation Specification

A transformation describes an operation that takes a list of input tensors and produces a list of output tensors.
[//]: # Stateful, stateless, do we care?

A confiuration entry in the bioimage.io model zoo is defined by a configuration file `<transformation name>.transformation.yaml`.
The configuration file must contain the [common keys](##Common Keys) and the keys `inputs`, `outputs` and `dependencies`.

### `inputs`
Describes the input tensors expected by this transformation.
Either a string from the following choices:
  - any: any number/shape of input tensors is accepted/returned

or a list of [tensor specifications](#tensor-specification).

### `outputs`
Either a string from the following choices:
  - any: any number/shape of input tensors is accepted/returned
  - identity: number/shape of output tensors is the same as input tensors
  - same number: same number of tensors as given to input is returned (shape may differ)

or a list of [tensor specifications](#tensor-specification).

#### tensor specification
Specification of a tensor.
- `name`: tensor name
- `axes`: string of axes identifiers, e.g. btczyx
- `data_type`: data type (e.g. float32)
- `data_range`: tuple of (minimum, maximum)
- [shape]: optional specification of tensor shape
     - Either
       - `min`: minimum shape with same length as `axes`.
       - `step`: minimum shape change with same length as `axes`. 
     - or
       - `exact`: exact shape (or list thereof) with same lenght as `axes`

### `dependencies`

Dependency manager and dependency file, specified as <dependency manager>:<relative path to file>
For example:
- conda:./environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

[//]: #`I am not quite sure what we decided on for the uri identifiers in the end, I am sticking with the simplest option for now
[//]: # <format>+<protocoll>://<path>`, e.g.: `conda+file://./req.txt`


## Model Specification

A model entry in the bioimage.io model zoo is defined by a configuration file `<model name>.model.yaml`.
The configuration file must contain the [common keys](## Common Keys and the keys `test_input`, test_output, `inputs`, `outputs,` `prediction`, `training`.
It may contain the key `thumbnail`. Note that only the model specification contains test data, for all other implementations, we assume that the underlying components are sufficiently tested and we just perform one integration test for running the model.

### `test_input`
Relative file path to test input. `language` and the file extension define its memory representation.
The input is always stored as list of tensors.

### `test_output`
Relative file path to test output. `language` and the file extension define its memory representation.
The input is always stored as list of tensors.

### `thumbnail`
Image that will be displayed on the Model Zoo website to represent this Model.

### `inputs`
Describes the input tensors expected by this model.
Must be a list of [tensor specifications](#tensor-specification).

[//]: # Force this to be explicit, or also allow any?

### `outputs`
Describes the output tensors from this model.
Must be a list of [tensor specifications](#tensor-specification).

[//]: # Force this to be explicit, or also allow any, identity, same?

### `prediction`
Specification of prediction for the model. Must cotain the following keys:
- `weights`: model weights to load for prediction, that were obtained by the training processs described in [training](### training).
  `source`: link to the model weight file. Preferably a zenode doi.
  `hash`: hash of hash of the model weight file specified by `source`
- `preprocess`:  list of transformations applied before the model input. Can be null if no preprocsssing is necessary. List entries must adhere to the [transformation entry](### transformation entry) format.
- `postprocess`: list of transformations applied after the model input. Can be null if no preprocessing is necessary. List entries must adhere to the [transformation entry] format.
- `dependencies`: dependencies required to run prediction. See [transformation config](## Transformation specification).

### transformation entry
Must be a dictionary with the key `spec`: relative path or link to a [transformation specification](## Transformation specification) file. The relative path must be specified as `file:./some/my_trafo.transformation.yaml`. The link as `https://https::github.com/some_repo/some_file/my_other_trafo.transformation.yaml`.
[//]: # Is this the correct URI format now?

Can contain the key `kwargs`: instantiation of keyword arguments for this transformation.

### `training`
Specification of training process used to obtain the model weights. Must contain the following keys:
- `source`: Implementation of the training process. Can either be a relative file and 
- `kwargs`: Keyword arguments for the training implementation, that are not part of `setup`.
- `setup`: The training set-up that is instantiated by the training function. It must contain the keys listed belows (for which we will provide parser functions.) It can consist additional keys, which needs to be parsed separately and may be used to extend the core library.
    - `reader`: specification of a [reader config](## Reader Specification).
    - `sampler`: specification of a [sampler config](## Sampler Specification).
    - `preprocess`: list of [transformation entries](### transformation entry) that are applied before tensors are fed to the model. 
    - `loss`: transformations that are applied to model outputs and loss.  list of [transformation entries](`### transformation entries`). Last entry must be the actual loss.
    - `optimizer`: optimizer used in training. For now, we have no specification for this, but just use the framework specific implementation directly. We may want to change this.
      - `source`: Implementation of the optimizer. As usual, either relative path or importable from dependencies.
      - `kwargs`: keyword arguments for the optimizer


## Reader Specification

A reader entry in the bioimage.io model zoo is defined by a configuration file `<reader name>.reader.yaml`.
A reader implements access to data. A reader can read from one or multiple data-sets.
It implements an interface that allows random access to arbitrary sub-tensors of the data-set.
Data CAN be private!

The reader config must contain the [common keys](## Common keys) and the key `dependencies`.


## Sampler Specification
A sampler entry in the bioimage.io model zoo is defined by a configuration file `<sampler name>.sampler.yaml`.
A sampler defines a sequence of batches over a reader. 

The sampler config must contain the [common keys](## Common keys), the key `dependencies` and `outputs`, see output description in [the transformation specifiaction](# Transformation Specification).


# Example Configurations

## Transformation

```yaml
[!INCLUDE[trafo config](./transformations/Sigmoid.transformation.yaml)]
```

## Model

```yaml
[!INCLUDE[model config](./models/Unet2dExample.model.yaml)]
```

##  Reader

```yaml
[!INCLUDE[reader config](./readers/nN5.reader.yaml)]
```

##  Sampler

```yaml
[!INCLUDE[sampler config](./samplers/RandomBatch.sampler.yaml)]
```