import org.apache.log4j.{Level, Logger}
import  org.apache.sedona.sql.utils.Adapter
import  org.apache.spark.sql.functions.{col, element_at, split}
import  org.apache.spark.sql.{DataFrame, Row, SparkSession, functions}
import  org.apache.spark.sql.types._

object ManageTrajectory {

  Logger.getLogger("org.spark_project").setLevel(Level.WARN)
  Logger.getLogger("org.apache").setLevel(Level.WARN)
  Logger.getLogger("akka").setLevel(Level.WARN)
  Logger.getLogger("com").setLevel(Level.WARN)


  def loadTrajectoryData(spark: SparkSession, filePath: String): DataFrame =
    {
      /* TO DO */
      val dfTrajectory = spark.read.option("multiline", "true").json(filePath)
      dfTrajectory.createOrReplaceTempView("dfTrajectory")
      var df = spark.sql("select trajectory_id,vehicle_id,trajectory.timestamp as Timestamp,trajectory.location as Location from dfTrajectory")
      df.createOrReplaceTempView("df")
      val df1 = spark.sql("select trajectory_id,vehicle_id,arrays_zip(Location,Timestamp) as points from df")
      df1.createOrReplaceTempView("df1")
      val df2 = spark.sql("select vehicle_id,trajectory_id,explode(points) from df1")
      df2.createOrReplaceTempView("df2")
      return df2
    }


  def getSpatialRange(spark: SparkSession, dfTrajectory: DataFrame, latMin: Double, lonMin: Double, latMax: Double, lonMax: Double): DataFrame =
  {
    /* TO DO */
    dfTrajectory.createOrReplaceTempView("df2")
    val df4 = spark.sql("select vehicle_id,trajectory_id,col['Location'] as loc,col['Timestamp'] as time from df2 where ST_Within(ST_point(col['Location'][1],col['Location'][0]),ST_PolygonFromEnvelope(" + (lonMin.toString) + "," + (latMin.toString) + "," + (lonMax.toString) + "," + (latMax.toString) + ")) order by col['Timestamp']")
    df4.createOrReplaceTempView("df4")
    val df5 = spark.sql("select trajectory_id,vehicle_id,collect_list(time) as timestamp,collect_list(loc) as location from df4 group by trajectory_id,vehicle_id ")
    df5.createOrReplaceTempView("df5")
    //df5.show()
    df5
  }


  def getSpatioTemporalRange(spark: SparkSession, dfTrajectory: DataFrame, timeMin: Long, timeMax: Long, latMin: Double, lonMin: Double, latMax: Double, lonMax: Double): DataFrame =
  {
    /* TO DO */
    dfTrajectory.createOrReplaceTempView("df2")
    val df4 = spark.sql("select vehicle_id,trajectory_id,col['Location'] as loc,col['Timestamp'] as time from df2 where ST_Within(ST_point(col['Location'][1],col['Location'][0]),ST_PolygonFromEnvelope(" + (lonMin.toString) + "," + (latMin.toString) + "," + (lonMax.toString) + "," + (latMax.toString) + ")) AND col['Timestamp'] BETWEEN " + (timeMin.toString) + " AND " + (timeMax.toString)+" order by col['Timestamp']")
    df4.createOrReplaceTempView("df4")
    val df5 = spark.sql("select trajectory_id,vehicle_id,collect_list(time) as timestamp,collect_list(loc) as location from df4 group by trajectory_id,vehicle_id")
    df5.createOrReplaceTempView("df5")
    //df5.show()
    df5
    // change the null to desired spark DataFrame object
  }


  def getKNNTrajectory(spark: SparkSession, dfTrajectory: DataFrame, trajectoryId: Long, neighbors: Int): DataFrame =
  {
    /* TO DO */
    dfTrajectory.createOrReplaceTempView("dfi")
    val df4 = spark.sql("select trajectory_id, vehicle_id, ST_GeomFromText(concat('MULTIPOINT(',concat_ws(',',collect_list(concat(string(col['Location'][1]), ' ', string(col['Location'][0])))),')')) as location from dfi group by trajectory_id,vehicle_id")
    df4.createOrReplaceTempView("df4")
    //df4.show()
    val df5 = spark.sql("select lc2.trajectory_id from df4 as lc1,df4 as lc2 where lc1.trajectory_id = "+ trajectoryId.toString +" AND lc1.trajectory_id <> lc2.trajectory_id order by ST_Distance(lc1.location,lc2.location) limit "+neighbors.toString)
    df5.createOrReplaceTempView("df5")
    //df5.show()
    df5 // change the null to desired spark DataFrame object
  }
}
