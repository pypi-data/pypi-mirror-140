# <img src="https://uploads-ssl.webflow.com/5ea5d3315186cf5ec60c3ee4/5edf1c94ce4c859f2b188094_logo.svg" alt="Pip.Services Logo" width="200"> <br/> Component definitions for Python Changelog

## <a name="3.5.9"></a> 3.5.9 (2022-02-26)

### Feature 
* Added method rename to ConnectionUtils class

## <a name="3.5.8"></a> 3.5.8 (2022-02-23)

### Bug fixes
* Fixed MemoryCredentialStore.lookup method

## <a name="3.5.7"></a> 3.5.7 (2022-01-28)

### Bug fixes
* Fixed MemoryDiscovery class

## <a name="3.5.5-3.5.6"></a> 3.5.5-3.5.6 (2022-01-26)

### Features
* Removed pybars3 dependency. Added pip_services3_expressions instead.
* Updated dependencies. 

### Bug fixes
* Fixed YAML dependency

## <a name="3.5.3-3.5.4"></a> 3.5.3-3.5.4 (2021-11-15)

### Bug fixes
* Fixed credential store descriptor name
* Fixed MemoryCredentialStore.lookup

## <a name="3.5.1-3.5.2"></a> 3.5.1-3.5.2 (2021-11-05)

### Bug fixes
* Fixed shutdown callback
* Added locks for Chached loggers, tracers, counters

## <a name="3.5.0"></a> 3.5.0 (2021-10-25)

Added state management components

### Bug fixes
* Specify versions for requirements

### Features
* Update imports
* **state** Added IStateStore interface and StateValue class
* **state** Added NullStateStore class
* **trace** Added MemoryStateStore class
* **trace** Added DefaultStateStoreFactory class

## <a name="3.4.3"></a> 3.4.3 (2021-09-05)

### Bug fixes
* Fixed protected methods for **config** module


## <a name="3.4.2"></a> 3.4.2 (2021-08-03)

### Bug fixes
* Fixed types in Lock package

## <a name="3.4.1"></a> 3.4.1 (2021-08-03)

### Bug fixes
* fixed ChachedCounters increment method
* fixed Logger compose error


## <a name="3.4.0"></a> 3.4.0 (2021-05-05)

### Bug fixes
* fixed names of private, protected and public properties and methods
* fixed interfaces method names
* fixed CompositeFactory.can_create

### Features
* added type hints
* CacheEntry added methods:
    - get_key
    - get_value
    - get_expiration
* fixed initialization of default factories and child classes
* Logger added get_source, set_source methods
* CacheCounter added get_interval, set_interval methods
* CachedLogger add max_cache_size param


## <a name="3.3.0"></a> 3.3.0 (2021-04-12)

### Features
* **trace** Added NullTracer class
* **trace** Added LogTracer class
* **trace** Added CachedTracer class
* **trace** Added CompositeTracer class
* Added tracer to Component class
* **connect** Added CompositeConnectionResolver class
* **connect** Added ConnectionUtils class

## <a name="3.2.2"></a> 3.2.2 (2021-03-08)

### Bug Fixes
* Logger fix %s strings

## <a name="3.2.1"></a> 3.2.1 (2020-12-24)

### Features
added **Test** module

## <a name="3.2.0"></a> 3.2.0 (2020-12-21)

### Features
added **Lock** module

### Breaking changes
* **ConfigReader** rename _read_config methods to _read_config

### Bug Fixes
* fixed Logger output args
* fixed imports


## <a name="3.1.1"></a> 3.1.1 (2020-08-01)
* Fixed issues

## <a name="3.0.0"></a> 3.0.0 (2018-10-30)

### New release
* Initial public release

### Features
- **Auth** - authentication credential stores
- **Build** - component factories framework
- **Cache** - distributed cache
- **Config** - configuration framework
- **Connect** - connection discovery services
- **Count** - performance counters components
- **Info** - context info
- **Log** - logging components