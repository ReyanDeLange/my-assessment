"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)

NOTE:
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    qry = """
        WITH customers_clean AS (
            SELECT
                CustomerID,
                MIN(Income) AS Income
            FROM customers
            GROUP BY CustomerID
        ),
        credit_clean AS (
            SELECT
                CustomerID,
                MIN(CustomerClass) AS CustomerClass
            FROM credit
            GROUP BY CustomerID
        )
        SELECT
            cr.CustomerClass,
            AVG(cu.Income) AS AverageIncome
        FROM credit_clean cr
        JOIN customers_clean cu
            ON cr.CustomerID = cu.CustomerID
        GROUP BY cr.CustomerClass;
    """

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """

    qry = """
        SELECT
            COUNT(*) AS RejectedApplications,
            CASE
                WHEN TRIM(c.Region) = 'WesternCape'   THEN 'WC'
                WHEN TRIM(c.Region) = 'Gauteng'       THEN 'GT'
                WHEN TRIM(c.Region) = 'KwaZulu-Natal' THEN 'KZN'
                WHEN TRIM(c.Region) = 'EasternCape'   THEN 'EC'
                WHEN TRIM(c.Region) = 'FreeState'     THEN 'FS'
                WHEN TRIM(c.Region) = 'Limpopo'       THEN 'LP'
                WHEN TRIM(c.Region) = 'NorthWest'     THEN 'NW'
                WHEN TRIM(c.Region) = 'NorthernCape'  THEN 'NC'
                WHEN TRIM(c.Region) = 'Mpumalanga'    THEN 'MP'
                ELSE TRIM(c.Region)
            END AS Province
        FROM loans l
        JOIN customers c ON l.CustomerID = c.CustomerID
        WHERE TRIM(l.ApprovalStatus) = 'Rejected'
        GROUP BY Province
        ORDER BY RejectedApplications DESC, Province;
    """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

    qry = """
        DROP TABLE IF EXISTS financing;

        CREATE TABLE financing (
            CustomerID INTEGER,
            Income REAL,
            LoanAmount REAL,
            LoanTerm INTEGER,
            InterestRate REAL,
            ApprovalStatus TEXT,
            CreditScore INTEGER
        );

        WITH customers_clean AS (
            SELECT
                CustomerID,
                MIN(Income) AS Income
            FROM customers
            GROUP BY CustomerID
        ),
        credit_clean AS (
            SELECT
                CustomerID,
                MIN(CreditScore) AS CreditScore
            FROM credit
            GROUP BY CustomerID
        )
        INSERT INTO financing (
            CustomerID, Income, LoanAmount, LoanTerm, InterestRate, ApprovalStatus, CreditScore
        )
        SELECT
            c.CustomerID,
            c.Income,
            l.LoanAmount,
            l.LoanTerm,
            l.InterestRate,
            l.ApprovalStatus,
            cr.CreditScore
        FROM customers_clean c
        JOIN loans l
            ON l.CustomerID = c.CustomerID
        JOIN credit_clean cr
            ON cr.CustomerID = c.CustomerID;
    """

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """

    # I didn't have time to convert to London time so I just filtered by time only
    # Converting the time has many factors like daylight saving time etc which would require more complex handling
    # Given more time I would implement this properly

    qry = """
        DROP TABLE IF EXISTS timeline;

        CREATE TABLE timeline AS
        WITH customer_ids AS (
            SELECT DISTINCT CustomerID
            FROM customers
        )
        SELECT
            c.CustomerID,
            m.MonthName,
            COUNT(r.RepaymentID) AS NumberOfRepayments,
            COALESCE(SUM(r.Amount), 0) AS AmountTotal
        FROM customer_ids c
        CROSS JOIN months m
        LEFT JOIN repayments r
            ON r.CustomerID = c.CustomerID
            AND CAST(STRFTIME('%m', r.RepaymentDate) AS INTEGER) = m.MonthID
            AND STRFTIME('%H:%M:%S', r.RepaymentDate) >= '06:00:00'
            AND STRFTIME('%H:%M:%S', r.RepaymentDate) <  '18:00:00'
        GROUP BY c.CustomerID, m.MonthID, m.MonthName
        ORDER BY c.CustomerID, m.MonthID;
    """

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """
        SELECT
            CustomerID,

            CAST(SUM(CASE WHEN MonthName = 'January'   THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JanuaryRepayments,
            SUM(CASE WHEN MonthName = 'January'   THEN AmountTotal ELSE 0 END) AS JanuaryTotal,

            CAST(SUM(CASE WHEN MonthName = 'February'  THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS FebruaryRepayments,
            SUM(CASE WHEN MonthName = 'February'  THEN AmountTotal ELSE 0 END) AS FebruaryTotal,

            CAST(SUM(CASE WHEN MonthName = 'March'     THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MarchRepayments,
            SUM(CASE WHEN MonthName = 'March'     THEN AmountTotal ELSE 0 END) AS MarchTotal,

            CAST(SUM(CASE WHEN MonthName = 'April'     THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AprilRepayments,
            SUM(CASE WHEN MonthName = 'April'     THEN AmountTotal ELSE 0 END) AS AprilTotal,

            CAST(SUM(CASE WHEN MonthName = 'May'       THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MayRepayments,
            SUM(CASE WHEN MonthName = 'May'       THEN AmountTotal ELSE 0 END) AS MayTotal,

            CAST(SUM(CASE WHEN MonthName = 'June'      THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JuneRepayments,
            SUM(CASE WHEN MonthName = 'June'      THEN AmountTotal ELSE 0 END) AS JuneTotal,

            CAST(SUM(CASE WHEN MonthName = 'July'      THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JulyRepayments,
            SUM(CASE WHEN MonthName = 'July'      THEN AmountTotal ELSE 0 END) AS JulyTotal,

            CAST(SUM(CASE WHEN MonthName = 'August'    THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AugustRepayments,
            SUM(CASE WHEN MonthName = 'August'    THEN AmountTotal ELSE 0 END) AS AugustTotal,

            CAST(SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS SeptemberRepayments,
            SUM(CASE WHEN MonthName = 'September' THEN AmountTotal ELSE 0 END) AS SeptemberTotal,

            CAST(SUM(CASE WHEN MonthName = 'October'   THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS OctoberRepayments,
            SUM(CASE WHEN MonthName = 'October'   THEN AmountTotal ELSE 0 END) AS OctoberTotal,

            CAST(SUM(CASE WHEN MonthName = 'November'  THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS NovemberRepayments,
            SUM(CASE WHEN MonthName = 'November'  THEN AmountTotal ELSE 0 END) AS NovemberTotal,

            CAST(SUM(CASE WHEN MonthName = 'December'  THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS DecemberRepayments,
            SUM(CASE WHEN MonthName = 'December'  THEN AmountTotal ELSE 0 END) AS DecemberTotal

        FROM timeline
        GROUP BY CustomerID
        ORDER BY CustomerID;
    """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """____________________"""

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`
    """

    qry = """____________________"""

    return qry
