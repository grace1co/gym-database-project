-- ITC 341
-- Gym Membership Database Project

-- drop tables if they exist
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE CheckIn CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE Membership CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE Member CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE Plan CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE GymLocation CASCADE CONSTRAINTS';
EXCEPTION
    WHEN OTHERS THEN NULL;
END;
/

CREATE TABLE GymLocation(
    GymID NUMBER(5) PRIMARY KEY,
    GymName VARCHAR2(50) NOT NULL
);

CREATE TABLE Member (
    MemberID NUMBER(5) PRIMARY KEY,
    Name VARCHAR2(50) NOT NULL,
    HomeGymID NUMBER(5),
    CONSTRAINT member_homegym_fk FOREIGN KEY (HomeGymID)
        REFERENCES GymLocation(GymID)
);

CREATE TABLE Plan(
    PlanID NUMBER(3) PRIMARY KEY,
    PlanName VARCHAR2(30) NOT NULL UNIQUE,
    AllowsGuest CHAR(1) DEFAULT 'N',
    CONSTRAINT plan_guest_ck CHECK (AllowsGuest IN ('Y','N'))
);

CREATE TABLE Membership (
    MembershipID NUMBER(5) PRIMARY KEY,
    MemberID NUMBER(5) NOT NULL,
    PlanID NUMBER(3) NOT NULL,
    Status VARCHAR2(10) DEFAULT 'ACTIVE',
    CONSTRAINT membership_member_fk FOREIGN KEY (MemberID)
        REFERENCES Member(MemberID),
    CONSTRAINT membership_plan_fk FOREIGN KEY (PlanID)
        REFERENCES Plan(PlanID),
    CONSTRAINT membership_status_ck CHECK (Status IN ('ACTIVE','EXPIRED','CANCELLED'))
);

CREATE TABLE CheckIn(
    CheckInID NUMBER(8) PRIMARY KEY,
    MemberID NUMBER(5) NOT NULL,
    GymID NUMBER(5) NOT NULL,
    CheckInTime TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT checkin_member_fk FOREIGN KEY (MemberID)
        REFERENCES Member(MemberID),
    CONSTRAINT checkin_gym_fk FOREIGN KEY (GymID)
        REFERENCES GymLocation(GymID)
);

-- view for active members
CREATE OR REPLACE VIEW ActiveMembers AS
SELECT m.MemberID, m.Name, p.PlanName, ms.Status
FROM Member m
JOIN Membership ms ON m.MemberID = ms.MemberID
JOIN Plan p ON ms.PlanID = p.PlanID
WHERE ms.Status = 'ACTIVE';

-- trigger to make sure member is active before checking in
CREATE OR REPLACE TRIGGER trg_active_checkin
BEFORE INSERT ON CheckIn
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM Membership
    WHERE MemberID = :NEW.MemberID
      AND Status = 'ACTIVE';

    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Member does not have an active membership');
    END IF;
END;
/

-- base data
INSERT INTO GymLocation VALUES (1, 'Planet Fitness Downtown');
INSERT INTO GymLocation VALUES (2, 'Planet Fitness Westside');

INSERT INTO Plan VALUES (1, 'Basic', 'N');
INSERT INTO Plan VALUES (2, 'Black Card', 'Y');

INSERT INTO Member VALUES (1001, 'Bob Smith', 1);
INSERT INTO Member VALUES (1002, 'Carol Davis', 2);

INSERT INTO Membership VALUES (5001, 1001, 2, 'ACTIVE');
INSERT INTO Membership VALUES (5002, 1002, 1, 'EXPIRED');

-- 100 extra members
BEGIN
    FOR i IN 3..102 LOOP
        INSERT INTO Member (MemberID, Name, HomeGymID)
        VALUES (
            1000 + i,
            CASE MOD(i, 20)
                WHEN 0 THEN 'Maya Johnson'
                WHEN 1 THEN 'James Smith'
                WHEN 2 THEN 'Maria Garcia'
                WHEN 3 THEN 'Robert Johnson'
                WHEN 4 THEN 'Linda Williams'
                WHEN 5 THEN 'Michael Brown'
                WHEN 6 THEN 'Barbara Jones'
                WHEN 7 THEN 'William Miller'
                WHEN 8 THEN 'Elizabeth Davis'
                WHEN 9 THEN 'David Garcia'
                WHEN 10 THEN 'Jennifer Rodriguez'
                WHEN 11 THEN 'Richard Martinez'
                WHEN 12 THEN 'Susan Wilson'
                WHEN 13 THEN 'Thomas Anderson'
                WHEN 14 THEN 'Lisa Taylor'
                WHEN 15 THEN 'Daniel Martin'
                WHEN 16 THEN 'Karen Lee'
                WHEN 17 THEN 'Anthony White'
                WHEN 18 THEN 'Sandra Clark'
                ELSE 'Taylor Brooks'
            END || ' ' || i,
            CASE WHEN MOD(i,2)=0 THEN 1 ELSE 2 END
        );
    END LOOP;
END;
/

-- 100 matching memberships with active / expired / cancelled variation
BEGIN
    FOR i IN 3..102 LOOP
        INSERT INTO Membership (MembershipID, MemberID, PlanID, Status)
        VALUES (
            5000 + i,
            1000 + i,
            CASE WHEN MOD(i,2)=0 THEN 1 ELSE 2 END,
            CASE
                WHEN MOD(i,10)=0 THEN 'CANCELLED'
                WHEN MOD(i,5)=0 THEN 'EXPIRED'
                ELSE 'ACTIVE'
            END
        );
    END LOOP;
END;
/

-- check-in data for the presentation queries
INSERT INTO CheckIn VALUES (1, 1001, 1, SYSTIMESTAMP);
INSERT INTO CheckIn VALUES (101, 1001, 1, SYSTIMESTAMP - 4);
INSERT INTO CheckIn VALUES (102, 1001, 1, SYSTIMESTAMP - 3);
INSERT INTO CheckIn VALUES (103, 1001, 2, SYSTIMESTAMP - 2);
INSERT INTO CheckIn VALUES (104, 1001, 1, SYSTIMESTAMP - 1);

INSERT INTO CheckIn VALUES (105, 1004, 2, SYSTIMESTAMP - 3);
INSERT INTO CheckIn VALUES (106, 1004, 2, SYSTIMESTAMP - 1);

INSERT INTO CheckIn VALUES (107, 1003, 1, SYSTIMESTAMP - 5);
INSERT INTO CheckIn VALUES (108, 1003, 1, SYSTIMESTAMP - 2);

INSERT INTO CheckIn VALUES (110, 1007, 1, SYSTIMESTAMP);
INSERT INTO CheckIn VALUES (111, 1009, 1, SYSTIMESTAMP);
INSERT INTO CheckIn VALUES (112, 1013, 1, SYSTIMESTAMP);

-- add 100 more check-ins for active members only
DECLARE
    v_member_id Member.MemberID%TYPE;
BEGIN
    FOR i IN 200..299 LOOP
        SELECT MemberID
        INTO v_member_id
        FROM (
            SELECT MemberID, ROW_NUMBER() OVER (ORDER BY MemberID) AS rn
            FROM Membership
            WHERE Status = 'ACTIVE'
        )
        WHERE rn = 1 + MOD(i, 81);

        INSERT INTO CheckIn (CheckInID, MemberID, GymID, CheckInTime)
        VALUES (
            i,
            v_member_id,
            CASE WHEN MOD(i,2)=0 THEN 1 ELSE 2 END,
            SYSTIMESTAMP - NUMTODSINTERVAL(MOD(i,48), 'HOUR')
        );
    END LOOP;
END;
/

COMMIT;

PROMPT ==== ROW COUNTS ====
SELECT COUNT(*) AS TotalMembers FROM Member;
SELECT COUNT(*) AS TotalMemberships FROM Membership;
SELECT COUNT(*) AS TotalCheckIns FROM CheckIn;

PROMPT ==== MEMBERSHIP STATUS TOTALS ====
SELECT Status, COUNT(*) AS Total
FROM Membership
GROUP BY Status
ORDER BY Status;

PROMPT ==== QUERY 1: THE ULTIMATE GYM RAT ====
SELECT m.Name, COUNT(c.CheckInID) AS TotalWorkouts
FROM Member m
JOIN CheckIn c ON m.MemberID = c.MemberID
GROUP BY m.Name
ORDER BY TotalWorkouts DESC
FETCH FIRST 1 ROWS ONLY;

PROMPT ==== QUERY 2: MOST CROWDED LOCATION ====
SELECT g.GymName, COUNT(c.CheckInID) AS FootTraffic
FROM GymLocation g
LEFT JOIN CheckIn c ON g.GymID = c.GymID
GROUP BY g.GymName
ORDER BY FootTraffic DESC
FETCH FIRST 1 ROWS ONLY;

PROMPT ==== QUERY 3: GUEST PRIVILEGES ====
SELECT m.Name, p.PlanName
FROM Member m
JOIN Membership ms ON m.MemberID = ms.MemberID
JOIN Plan p ON ms.PlanID = p.PlanID
WHERE p.AllowsGuest = 'Y'
  AND ms.Status = 'ACTIVE'
FETCH FIRST 10 ROWS ONLY;

PROMPT ==== QUERY 4: EXPIRED MEMBERS ====
SELECT m.Name, ms.Status
FROM Member m
JOIN Membership ms ON m.MemberID = ms.MemberID
WHERE ms.Status = 'EXPIRED'
FETCH FIRST 10 ROWS ONLY;

PROMPT ==== TRIGGER TEST: THIS SHOULD FAIL ====
INSERT INTO CheckIn VALUES (999, 1002, 2, SYSTIMESTAMP);