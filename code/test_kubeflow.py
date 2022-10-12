import kfp
from kfp import dsl

def add_two_numbers(a, b):
  return dsl.ContainerOp(
    name='calculate_sum',
    image='python:3.6.8',
    command=['python', '-c'],
    arguments=['with open("/tmp/results.txt", "a") as file: file.write(str({} + {}))'.format(a, b)],
    file_outputs={
      'data': '/tmp/results.txt',
    }
  )

def echo_op(text):
  return dsl.ContainerOp(
    name='echo',
    image='library/bash:4.4.23',
    command=['sh', '-c'],
    arguments=[
      'echo "Result: {}"'.format(text)
    ],
  )

@dsl.pipeline(
  name='Calculate sum pipeline',
  description='Calculate the sum of numbers and print the results'
)
def calculate_sum(a=7, b=10, c=4, d=7):
  sum1 = add_two_numbers(a, b)
  sum2 = add_two_numbers(c, d)
  sum = add_two_numbers(sum1.output, sum2.output)

  echo_op(sum.output)

kfp.compiler.Compiler().compile(pipeline_func=calculate_sum, package_path='/Users/pat/dev/cramer_bot/yamls/pipeline.yaml')

client = kfp.Client(host='http://localhost:3000')
experiment = client.create_experiment(name='kubeflow')
my_run = client.run_pipeline(
  experiment_id=experiment.id,
  job_name='calculate-sum',
  pipeline_package_path='/Users/pat/dev/cramer_bot/yamls/pipeline.yaml'
)

print(f"Run {my_run.id} started...")
client.wait_for_run_completion(my_run.id, timeout=3600)
complete_run = client.get_run(my_run.id)
print(f"Run {my_run.id} state: {complete_run.run.status}")