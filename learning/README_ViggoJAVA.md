# DuckLake Local Lab Tutorial

This lab teaches you how to create a local DuckLake from a Java application and then read that same DuckLake through a small Spring Boot API.

The lab has two parts:

```text
Part 1: Java application -> DuckLake -> CRUD operations
Part 2: Browser/API request -> Spring Boot -> DuckLake -> JSON response
```

The focus of the lab is DuckLake. Spring Boot is only used in Part 2 to show how an application can expose DuckLake data through an API.

By the end of the lab, you will have built an application that can:

1. create a local DuckLake,
2. create a table,
3. insert rows,
4. read rows,
5. update rows,
6. delete rows,
7. expose the DuckLake data through HTTP endpoints.

---

## 1. What you will build

The application will create a local DuckLake in a generated `data/` folder:

```text
catalog:      data/local_ducklake.ducklake
data files:   data/files/
```

DuckLake separates metadata from data:

```text
Catalog/metadata:
Stores information about tables, schemas, snapshots, and which data files belong to the tables.

Data files:
Stores the actual table data.
```

In this lab, the DuckLake catalog is stored in:

```text
data/local_ducklake.ducklake
```

and the table data is stored in:

```text
data/files/
```

You will first use DuckLake directly from Java. Then you will build a Spring Boot API that reads from the same local DuckLake.

---

## 2. Requirements

Before starting, make sure you have:

- Java 21
- Maven
- IntelliJ IDEA or another Java IDE
- An internet connection the first time DuckDB installs the DuckLake extension

---

# Part 1: Create a local DuckLake and perform CRUD

In Part 1, you will build a normal Java application that connects to DuckDB, attaches a local DuckLake, and performs CRUD operations.

CRUD means:

```text
C = Create
R = Read
U = Update
D = Delete
```

In SQL, this usually means:

```text
CREATE TABLE
INSERT INTO
SELECT
UPDATE
DELETE
```

---

## 3. Create a new Java project

Create a new Java project with these settings:

```text
Name: ducklake-local-lab
Build system: Maven
JDK: Java 21
GroupId: se.kth.ducklake
ArtifactId: ducklake-local-lab
```

The project should have this structure:

```text
ducklake-local-lab/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── se/
                └── kth/
                    └── ducklake/
                        └── Main.java
```

The Java package should be:

```java
package se.kth.ducklake;
```

---

## 4. Add the DuckDB JDBC dependency

Open `pom.xml` and replace its content with this:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">

    <modelVersion>4.0.0</modelVersion>

    <groupId>se.kth.ducklake</groupId>
    <artifactId>ducklake-local-lab</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.duckdb</groupId>
            <artifactId>duckdb_jdbc</artifactId>
            <version>1.5.2.0</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>exec-maven-plugin</artifactId>
                <version>3.3.0</version>
                <configuration>
                    <mainClass>se.kth.ducklake.Main</mainClass>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

Reload Maven after editing `pom.xml`.

---

## 5. Create the first version of `Main.java`

Open:

```text
src/main/java/se/kth/ducklake/Main.java
```

Start with this simple program:

```java
package se.kth.ducklake;

public class Main {
    public static void main(String[] args) {
        System.out.println("DuckLake local lab started");
    }
}
```

Run the program from `Main`.

Expected output:

```text
DuckLake local lab started
```

If you see this output, your Java project is working.

---

## 6. Add imports and constants

At the top of `Main.java`, add these imports under the package declaration:

```java
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.*;
```

Inside the `Main` class, add these constants:

```java
private static final String DUCKLAKE_CATALOG = "data/local_ducklake.ducklake";
private static final String DUCKLAKE_FILES = "data/files/";
```

Your file should now begin like this:

```java
package se.kth.ducklake;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.*;

public class Main {

    private static final String DUCKLAKE_CATALOG = "data/local_ducklake.ducklake";
    private static final String DUCKLAKE_FILES = "data/files/";

    public static void main(String[] args) {
        System.out.println("DuckLake local lab started");
    }
}
```

The `DUCKLAKE_CATALOG` path is where DuckLake metadata will be stored.

The `DUCKLAKE_FILES` path is where the actual table data will be stored.

---

## 7. Create local folders for DuckLake

Before DuckLake can store files locally, the application should create the folders it needs.

Add this method inside the `Main` class:

```java
private static void setupFolders() throws Exception {
    Files.createDirectories(Path.of("data"));
    Files.createDirectories(Path.of(DUCKLAKE_FILES));
}
```

Now update your `main` method:

```java
public static void main(String[] args) {
    try {
        setupFolders();
        System.out.println("Folders created");
    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

Run the program from `Main`.

Expected output:

```text
Folders created
```

A new folder called `data/` should now appear in your project.

---

## 8. Connect to DuckDB from Java

DuckLake is used through DuckDB, so the Java program first needs a DuckDB connection.

Update your `main` method:

```java
public static void main(String[] args) {
    try {
        setupFolders();

        try (Connection conn = DriverManager.getConnection("jdbc:duckdb:")) {
            System.out.println("Connected to DuckDB");
        }

    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

Run the program from `Main`.

Expected output:

```text
Connected to DuckDB
```

The connection string:

```java
DriverManager.getConnection("jdbc:duckdb:")
```

creates a DuckDB session from Java.

---

## 9. Install, load, and attach DuckLake

Now add a method that prepares DuckLake.

Add this method inside the `Main` class:

```java
private static void setupDuckLake(Connection conn) throws SQLException {
    try (Statement stmt = conn.createStatement()) {
        stmt.execute("INSTALL ducklake");
        stmt.execute("LOAD ducklake");

        stmt.execute("""
            ATTACH 'ducklake:%s' AS local_lake
            (DATA_PATH '%s')
            """.formatted(DUCKLAKE_CATALOG, DUCKLAKE_FILES));

        stmt.execute("USE local_lake");
    }
}
```

Then update your `main` method:

```java
public static void main(String[] args) {
    try {
        setupFolders();

        try (Connection conn = DriverManager.getConnection("jdbc:duckdb:")) {
            setupDuckLake(conn);
            System.out.println("DuckLake is ready");
        }

    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

Run the program from `Main`.

Expected output:

```text
DuckLake is ready
```

This is one of the most important parts of the lab.

These two lines make the DuckLake extension available:

```java
stmt.execute("INSTALL ducklake");
stmt.execute("LOAD ducklake");
```

This line creates or connects to a local DuckLake:

```sql
ATTACH 'ducklake:data/local_ducklake.ducklake' AS local_lake
(DATA_PATH 'data/files/')
```

This line selects the DuckLake as the active database:

```sql
USE local_lake
```

Without `USE local_lake`, later SQL statements may run against DuckDB's temporary in-memory database instead of the DuckLake.

---

## 10. Create the `students` table

Now create a table called `students`.

Add this method:

```java
private static void createTable(Connection conn) throws SQLException {
    try (Statement stmt = conn.createStatement()) {
        stmt.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER,
                name VARCHAR,
                program VARCHAR,
                credits INTEGER
            )
            """);
    }
}
```

Then call it from `main` after `setupDuckLake(conn)`:

```java
setupDuckLake(conn);
createTable(conn);
System.out.println("Table created");
```

Your `main` method should now contain:

```java
try (Connection conn = DriverManager.getConnection("jdbc:duckdb:")) {
    setupDuckLake(conn);
    createTable(conn);
    System.out.println("Table created");
}
```

Run the program from `Main`.

Expected output:

```text
Table created
```

DuckLake does not currently support primary key constraints, so `id` is used as a normal column in this beginner lab.

---

## 11. Insert rows into the table

Now add example data to the `students` table.

Add this method:

```java
private static void insertExampleData(Connection conn) throws SQLException {
    try (Statement clear = conn.createStatement()) {
        clear.execute("DELETE FROM students");
    }

    String sql = "INSERT INTO students (id, name, program, credits) VALUES (?, ?, ?, ?)";

    try (PreparedStatement stmt = conn.prepareStatement(sql)) {
        stmt.setInt(1, 1);
        stmt.setString(2, "Alice");
        stmt.setString(3, "Datateknik");
        stmt.setInt(4, 90);
        stmt.executeUpdate();

        stmt.setInt(1, 2);
        stmt.setString(2, "Bob");
        stmt.setString(3, "Medieteknik");
        stmt.setInt(4, 60);
        stmt.executeUpdate();

        stmt.setInt(1, 3);
        stmt.setString(2, "Charlie");
        stmt.setString(3, "Elektroteknik");
        stmt.setInt(4, 45);
        stmt.executeUpdate();
    }
}
```

Then call it from `main` after `createTable(conn)`:

```java
setupDuckLake(conn);
createTable(conn);
insertExampleData(conn);
System.out.println("Example data inserted");
```

Run the program from `Main`.

Expected output:

```text
Example data inserted
```

The method starts with:

```java
clear.execute("DELETE FROM students");
```

This clears the table before inserting example data.

This makes the output predictable every time you run the program.

---

## 12. Read and print rows

Now add a method that reads all students and prints them.

Add this method:

```java
private static void printStudents(Connection conn) throws SQLException {
    String sql = "SELECT id, name, program, credits FROM students ORDER BY id";

    try (
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(sql)
    ) {
        while (rs.next()) {
            System.out.printf(
                    "id=%d, name=%s, program=%s, credits=%d%n",
                    rs.getInt("id"),
                    rs.getString("name"),
                    rs.getString("program"),
                    rs.getInt("credits")
            );
        }
    }
}
```

Then call it from `main` after `insertExampleData(conn)`:

```java
System.out.println("\n--- After INSERT ---");
printStudents(conn);
```

Run the program from `Main`.

Expected output:

```text
--- After INSERT ---
id=1, name=Alice, program=Datateknik, credits=90
id=2, name=Bob, program=Medieteknik, credits=60
id=3, name=Charlie, program=Elektroteknik, credits=45
```

You have now completed the `Read` part of CRUD.

---

## 13. Update a row

Now add an update operation.

Add this method:

```java
private static void updateStudent(Connection conn, int id, String name, String program, int credits) throws SQLException {
    String sql = """
        UPDATE students
        SET name = ?, program = ?, credits = ?
        WHERE id = ?
        """;

    try (PreparedStatement stmt = conn.prepareStatement(sql)) {
        stmt.setString(1, name);
        stmt.setString(2, program);
        stmt.setInt(3, credits);
        stmt.setInt(4, id);
        stmt.executeUpdate();
    }
}
```

Then call it from `main` after printing the inserted rows:

```java
updateStudent(conn, 1, "Viggo", "Datateknik", 120);

System.out.println("\n--- After UPDATE ---");
printStudents(conn);
```

Run the program from `Main`.

Expected output after the update:

```text
--- After UPDATE ---
id=1, name=Viggo, program=Datateknik, credits=120
id=2, name=Bob, program=Medieteknik, credits=60
id=3, name=Charlie, program=Elektroteknik, credits=45
```

You have now completed the `Update` part of CRUD.

---

## 14. Delete a row

Now add a delete operation.

Add this method:

```java
private static void deleteStudent(Connection conn, int id) throws SQLException {
    String sql = "DELETE FROM students WHERE id = ?";

    try (PreparedStatement stmt = conn.prepareStatement(sql)) {
        stmt.setInt(1, id);
        stmt.executeUpdate();
    }
}
```

Then call it from `main` after the update step:

```java
deleteStudent(conn, 2);

System.out.println("\n--- After DELETE ---");
printStudents(conn);
```

Run the program from `Main`.

Expected output after the delete:

```text
--- After DELETE ---
id=1, name=Viggo, program=Datateknik, credits=120
id=3, name=Charlie, program=Elektroteknik, credits=45
```

You have now completed the `Delete` part of CRUD.

---

## 15. Check your final Part 1 `main` method

Your final Part 1 `main` method should follow this order:

```java
public static void main(String[] args) {
    try {
        setupFolders();

        try (Connection conn = DriverManager.getConnection("jdbc:duckdb:")) {
            setupDuckLake(conn);
            createTable(conn);
            insertExampleData(conn);

            System.out.println("\n--- After INSERT ---");
            printStudents(conn);

            updateStudent(conn, 1, "Viggo", "Datateknik", 120);

            System.out.println("\n--- After UPDATE ---");
            printStudents(conn);

            deleteStudent(conn, 2);

            System.out.println("\n--- After DELETE ---");
            printStudents(conn);
        }

    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

Run the application one final time from `Main`.

Expected output:

```text
--- After INSERT ---
id=1, name=Alice, program=Datateknik, credits=90
id=2, name=Bob, program=Medieteknik, credits=60
id=3, name=Charlie, program=Elektroteknik, credits=45

--- After UPDATE ---
id=1, name=Viggo, program=Datateknik, credits=120
id=2, name=Bob, program=Medieteknik, credits=60
id=3, name=Charlie, program=Elektroteknik, credits=45

--- After DELETE ---
id=1, name=Viggo, program=Datateknik, credits=120
id=3, name=Charlie, program=Elektroteknik, credits=45
```

If your output matches this, your local DuckLake CRUD application works.

At this point, the local DuckLake exists on disk in the `data/` folder. Part 2 will reuse that same DuckLake.

---

# Part 2: Read DuckLake data through a Spring Boot API

In Part 1, the Java program talked directly to DuckLake and printed the result in the terminal.

In Part 2, you will keep the same local DuckLake, but change the application structure:

```text
Before:
Main.java -> DuckLake -> terminal output

After:
Browser/API request -> Spring Boot controller -> DuckLakeService -> DuckLake -> JSON response
```

This is useful because real applications often do not just print database results in the terminal. They expose data through an API so that another application, browser, frontend, or service can use it.

This also prepares you for the later KTH Cloud tutorial, where the main goal is to read datasets from a shared DuckLake deployment.

In this local lab, we only expose read endpoints. CRUD was already covered in Part 1. Part 2 focuses on reading DuckLake data from an application API.

---

## 16. Convert the project to Spring Boot

Open `pom.xml` and replace its content with this:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">

    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.0.6</version>
        <relativePath/>
    </parent>

    <groupId>se.kth.ducklake</groupId>
    <artifactId>ducklake-local-lab</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <java.version>21</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webmvc</artifactId>
        </dependency>

        <dependency>
            <groupId>org.duckdb</groupId>
            <artifactId>duckdb_jdbc</artifactId>
            <version>1.5.2.0</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

Reload Maven after editing `pom.xml`.

The important change is that the project now includes Spring Boot and a web server.

The DuckDB JDBC dependency is still included, because the application still connects to DuckLake through DuckDB.

---

## 17. Replace `Main.java` with a Spring Boot main class

In Part 1, `Main.java` contained all the DuckLake logic.

In Part 2, `Main.java` should only start the Spring Boot application. The DuckLake logic will be moved to a separate service class.

Replace `Main.java` with this:

```java
package se.kth.ducklake;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Main {

    public static void main(String[] args) {
        SpringApplication.run(Main.class, args);
    }
}
```

This starts the Spring Boot application and keeps it running so it can answer HTTP requests.

---

## 18. Create the `Student` record

Create a new file:

```text
src/main/java/se/kth/ducklake/Student.java
```

Add this code:

```java
package se.kth.ducklake;

public record Student(int id, String name, String program, int credits) { }
```

This record represents one row in the `students` table.

Spring Boot can automatically convert a list of `Student` objects into JSON.

---

## 19. Create `DuckLakeService.java`

Create a new file:

```text
src/main/java/se/kth/ducklake/DuckLakeService.java
```

Add this code:

```java
package se.kth.ducklake;

import org.springframework.stereotype.Service;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

@Service
public class DuckLakeService {

    private static final String DUCKLAKE_CATALOG = "data/local_ducklake.ducklake";
    private static final String DUCKLAKE_FILES = "data/files/";

    public DuckLakeService() {
        try {
            setupFolders();

            try (Connection conn = openConnection()) {
                createStudentsTable(conn);
                insertExampleDataIfTableIsEmpty(conn);
            }
        } catch (Exception e) {
            throw new RuntimeException("Could not initialize DuckLake", e);
        }
    }

    private void setupFolders() throws Exception {
        Files.createDirectories(Path.of("data"));
        Files.createDirectories(Path.of(DUCKLAKE_FILES));
    }

    private Connection openConnection() throws SQLException {
        Connection conn = DriverManager.getConnection("jdbc:duckdb:");

        try {
            try (Statement stmt = conn.createStatement()) {
                stmt.execute("INSTALL ducklake");
                stmt.execute("LOAD ducklake");

                stmt.execute("""
                    ATTACH 'ducklake:%s' AS local_lake
                    (DATA_PATH '%s')
                    """.formatted(DUCKLAKE_CATALOG, DUCKLAKE_FILES));

                stmt.execute("USE local_lake");
            }

            return conn;
        } catch (SQLException e) {
            try {
                conn.close();
            } catch (SQLException ignored) {
            }

            throw e;
        }
    }

    private void createStudentsTable(Connection conn) throws SQLException {
        try (Statement stmt = conn.createStatement()) {
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER,
                    name VARCHAR,
                    program VARCHAR,
                    credits INTEGER
                )
                """);
        }
    }

    private void insertExampleDataIfTableIsEmpty(Connection conn) throws SQLException {
        try (
                Statement countStatement = conn.createStatement();
                ResultSet rs = countStatement.executeQuery("SELECT COUNT(*) FROM students")
        ) {
            if (rs.next() && rs.getInt(1) > 0) {
                return;
            }
        }

        insertStudent(conn, new Student(1, "Alice", "Datateknik", 90));
        insertStudent(conn, new Student(2, "Bob", "Medieteknik", 60));
        insertStudent(conn, new Student(3, "Charlie", "Elektroteknik", 45));
    }

    private void insertStudent(Connection conn, Student student) throws SQLException {
        String sql = "INSERT INTO students (id, name, program, credits) VALUES (?, ?, ?, ?)";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, student.id());
            stmt.setString(2, student.name());
            stmt.setString(3, student.program());
            stmt.setInt(4, student.credits());
            stmt.executeUpdate();
        }
    }

    public List<String> listDatasets() {
        String sql = "SHOW TABLES";
        List<String> datasets = new ArrayList<>();

        try (
                Connection conn = openConnection();
                Statement stmt = conn.createStatement();
                ResultSet rs = stmt.executeQuery(sql)
        ) {
            while (rs.next()) {
                datasets.add(rs.getString(1));
            }
        } catch (SQLException e) {
            throw new RuntimeException("Could not list datasets", e);
        }

        return datasets;
    }

    public List<Student> listStudents() {
        String sql = "SELECT id, name, program, credits FROM students ORDER BY id";
        List<Student> students = new ArrayList<>();

        try (
                Connection conn = openConnection();
                Statement stmt = conn.createStatement();
                ResultSet rs = stmt.executeQuery(sql)
        ) {
            while (rs.next()) {
                students.add(new Student(
                        rs.getInt("id"),
                        rs.getString("name"),
                        rs.getString("program"),
                        rs.getInt("credits")
                ));
            }
        } catch (SQLException e) {
            throw new RuntimeException("Could not list students", e);
        }

        return students;
    }
}
```

This class contains the DuckLake logic.

The most important idea is that the same DuckLake setup from Part 1 has now been moved from `Main.java` into `DuckLakeService`.

The service still does the same DuckLake steps:

```text
1. create local folders,
2. connect to DuckDB,
3. install and load DuckLake,
4. attach the local DuckLake,
5. use the local DuckLake,
6. query the students table.
```

The constructor also creates the `students` table if it does not exist.

If the table is empty, it inserts example data. If the table already contains data from Part 1, it keeps that data.

This means Part 2 reuses the DuckLake created in Part 1 instead of always resetting it.

---

## 20. Create `DuckLakeController.java`

Create a new file:

```text
src/main/java/se/kth/ducklake/DuckLakeController.java
```

Add this code:

```java
package se.kth.ducklake;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
public class DuckLakeController {

    private final DuckLakeService duckLakeService;

    public DuckLakeController(DuckLakeService duckLakeService) {
        this.duckLakeService = duckLakeService;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "ok");
    }

    @GetMapping("/datasets")
    public List<String> listDatasets() {
        return duckLakeService.listDatasets();
    }

    @GetMapping("/datasets/students")
    public List<Student> listStudentsDataset() {
        return duckLakeService.listStudents();
    }
}
```

This controller exposes three endpoints:

```text
GET /health
GET /datasets
GET /datasets/students
```

The controller does not contain SQL. It only receives HTTP requests and calls `DuckLakeService`.

This keeps the API layer separate from the DuckLake/database layer.

---

## 21. Run the Spring Boot application

Run the application from `Main`.

This time, the application should not stop immediately after printing output. It should keep running because Spring Boot starts a local web server.

When the application has started, it should be available at:

```text
http://localhost:8080
```

---

## 22. Test `/health`

Open this URL in a browser:

```text
http://localhost:8080/health
```

Expected response:

```json
{"status":"ok"}
```

This confirms that Spring Boot is running and can answer HTTP requests.

---

## 23. Test `/datasets`

Open this URL:

```text
http://localhost:8080/datasets
```

Expected response:

```json
["students"]
```

This endpoint asks DuckLake which tables are available.

In this lab, the table `students` is treated as a dataset.

---

## 24. Test `/datasets/students`

Open this URL:

```text
http://localhost:8080/datasets/students
```

If you completed Part 1 and did not delete the `data/` folder, you should see the final table state from Part 1:

```json
[
  {"id":1,"name":"Viggo","program":"Datateknik","credits":120},
  {"id":3,"name":"Charlie","program":"Elektroteknik","credits":45}
]
```

If your `data/` folder was empty before starting Part 2, the application will insert example data and you may instead see:

```json
[
  {"id":1,"name":"Alice","program":"Datateknik","credits":90},
  {"id":2,"name":"Bob","program":"Medieteknik","credits":60},
  {"id":3,"name":"Charlie","program":"Elektroteknik","credits":45}
]
```

Both results are valid.

The important point is that the data is read from the local DuckLake and returned as JSON through the Spring Boot API.

---

## 25. What Part 2 adds

Part 1 proved that Java can create and modify a local DuckLake.

Part 2 proves that an application can expose DuckLake data through an API.

The important change is:

```text
Part 1:
Java code directly queries DuckLake and prints results in the terminal.

Part 2:
A browser or another application sends a request to Spring Boot.
Spring Boot calls DuckLakeService.
DuckLakeService queries DuckLake.
The result is returned as JSON.
```

This is useful because many real applications need to read data from a database and provide it to a frontend, another service, or a user-facing API.

This is also close to the next step of the project: connecting an application to a shared DuckLake deployment in KTH Cloud and reading datasets from it.

---

## 26. Cleanup

To reset the local DuckLake, stop the application and delete the generated `data/` folder.

Then run the application again.

The application will create a new local DuckLake from scratch.

---

## 27. Next steps

This local lab has shown how to:

1. create a local DuckLake,
2. perform CRUD operations from Java,
3. read DuckLake data through a Spring Boot API.

A later tutorial can build on this by showing how to connect an application to a shared DuckLake deployment in KTH Cloud and read datasets from that deployment.

Another later part of the project can add a frontend where authenticated users can view, add, or delete datasets.
