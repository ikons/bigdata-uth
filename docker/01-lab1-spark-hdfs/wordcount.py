from pyspark import SparkConf
from pyspark.sql import SparkSession
conf = SparkConf().setAppName("Word Count example") \
    .set("spark.master", "spark://spark-master:7077") \
    .set("spark.executor.memory", "3g") \
    .set("spark.driver.memory", "512m")
sc = SparkSession.builder.config(conf=conf).getOrCreate().sparkContext
wordcount = sc.textFile("hdfs://namenode:9000/user/root/text.txt") \
    .flatMap(lambda x: x.split(" ")) \
    .map(lambda x: (x, 1)) \
    .reduceByKey(lambda x,y: x+y) \
    .sortBy(lambda x: x[1], ascending=False)
print(wordcount.collect())
wordcount.saveAsTextFile("hdfs://namenode:9000/user/root/wordcount-output")