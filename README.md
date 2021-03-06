# Causal Testing: A Causal Inference-Driven Framework for Functional Black-Box Testing

 ![example workflow](https://github.com/CITCOM-project/CausalTestingFramework/actions/workflows/ci-tests.yaml/badge.svg) [![codecov](https://codecov.io/gh/CITCOM-project/CausalTestingFramework/branch/main/graph/badge.svg?token=04ijFVrb4a)](https://codecov.io/gh/CITCOM-project/CausalTestingFramework)

Causal testing is a causal inference-driven framework for functional black-box testing. This framework utilises graphical causal inference (CI) techniques for the specification and functional testing of software from a black-box perspective. In this framework, we use causal directed acyclic graphs (DAGs) to express the anticipated cause-effect relationships amongst the inputs and outputs of the system-under-test and the supporting mathematical framework to design statistical procedures capable of making causal inferences. Each causal test case focuses on the causal effect of an intervention made to the system-under test. That is, a prescribed change to the input configuration of the system-under-test that is expected to cause a change to some output(s). 

![Causal Testing Workflow](images/workflow.png)

The causal testing framework has three core components:

1. [Causal specification](causal_testing/specification/README.md): Before we can test software, we need to obtain an understanding of how it should behave in a particular use-case scenario. In addition, to apply graphical CI techniques for testing, we need a causal DAG which depicts causal relationships amongst inputs and outputs. To collect this information, users must create a _causal specification_. This comprises a set of scenarios which place constraints over input variables that capture the use-case of interest, a causal DAG corresponding to this scenario, and a series of high-level functional requirements that the user wishes to test. In causal testing, these requirements should describe how the model should respond to interventions (changes made to the input configuration).

2. [Causal tests](causal_testing/testing/README.md): With a causal specification in hand, we can now go about designing a series of test cases that interrogate the causal relationships of interest in the scenario-under-test. Informally, a causal test case is a triple (X, Delta, Y), where X is an input configuration, Delta is an intervention which should be applied to X, and Y is the expected _causal effect_ of that intervention on some output of interest. Therefore, a causal test case states the expected causal effect (Y) of a particular intervention (Delta) made to an input configuration (X). For each scenario, the user should create a suite of causal tests. Once a causal test case has been defined, it is executed as follows:
    1. Using the causal DAG, identify an estimand for the effect of the intervention on the output of interest. That is, a statistical procedure capable of estimating the causal effect of the intervention on the output.
    2. Collect the data to which the statistical procedure will be applied (see Data collection below).
    3. Apply a statistical model (e.g. linear regression or causal forest) to the data to obtain a point estimate for the causal effect. Depending on the estimator used, confidence intervals may also be obtained at a specified confidence level e.g. 0.05 corresponds to 95% confidence intervals (optional).
    4. Return the casual test result as a 4-tuple: `(estimand, point_estimate, confidence_intervals, confidence_level)`
A test oracle procedure can then be implemented which takes the causal test result and determines whether the test should pass or fail. In the simplest case, this takes the form of an assertion which compares the point estimate to the expected causal effect specified in the causal test case.

3. [Data collection](causal_testing/data_collection/README.md): Data for the system-under-test can be collected in two ways: experimentally or observationally. The former involves executing the system-under-test under controlled conditions which, by design, isolate the causal effect of interest (accurate but expensive), while the latter involves collecting suitable previous execution data and utilising our causal knowledge to draw causal inferences (potentially less accurate but efficient). To collect experimental data, the user must implement a `collect_data` method which returns two csv files, one with the executions for the control case (intervention not applied), and one with the executions for the treatment case (intervention applied). On the other hand, when dealing with observational data, we need to check that the data is suitable for the identified estimand in two ways. First, we need to confirm that the data contains a column for each variable in the causal DAG. Second, we need to check that we have no [positivity violations](https://www.youtube.com/watch?v=4xc8VkrF98w). If there are positivity violations, we can provide instructions for an execution which will fill the gap.

For more information on each of these steps, follow the link to their respective documentation.

## Terminology
Here are some explanations for the terminology used above.

### Causal Inference
- Causal inference (CI) is a family of statistical techniques designed to quanitfy and establish **causal** relationships in data. In contrast to purely statistical techniques that are driven by associations in data, CI encorporates knowledge about the data-generating mechanisms behind relationships in data to derive causal conclusions. 
- One of the key advantages of CI is that it is possible to answer causal questions using **observational data**. That is, data which has been passively observed rather than collected from an experiment and, therefore, may contain all kinds of bias. In a testing context, we would like to leverage this advantage to test causal relationships in software without having to run costly experiments.
- There are many forms of CI techniques with slightly different aims, but in this framework we focus on graphical CI techniques that use directed acyclic graphs to obtain causal estimates. These approaches used a causal DAG to explain the causal relationships that exist in data and, based on the structure of this graph, design statistical experiments capable of estimating the causal effect of a particular intervention or action, such as taking a drug or changing the value of an input variable.

### Testing
- Functional testing is form of software testing that focuses on testing functional requirements (i.e. how the system-under-test should behave).
- Black-box testing if any form of testing that treats the system-under-test as a black-box, focusing on the inputs and outputs instead of the inner-workings.
