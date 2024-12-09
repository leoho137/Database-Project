DROP TABLE IF EXISTS Customer_Service;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS Datas;
DROP TABLE IF EXISTS Device;
DROP TABLE IF EXISTS ServiceLocation;
DROP TABLE IF EXISTS Model;
DROP TABLE IF EXISTS Price;
DROP TABLE IF EXISTS user;

CREATE TABLE user
(
    cid        INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50)        NOT NULL,
    last_name  VARCHAR(50)        NOT NULL,
    username   VARCHAR(50) UNIQUE NOT NULL,
    password   VARCHAR(1000)      NOT NULL,
    billAddr   VARCHAR(4000)      NOT NULL
);


CREATE TABLE ServiceLocation
(
    sLid          INT PRIMARY KEY AUTO_INCREMENT,
    addr          VARCHAR(50) NOT NULL,
    zipcode       INT         NOT NULL,
    unitNumber    VARCHAR(20) NOT NULL,
    tookOverDate  DATE        NOT NULL,
    squareFootage INT         NOT NULL,
    bedroomCnt    INT         NOT NULL,
    occupantsCnt  INT         NOT NULL
);

CREATE TABLE Customer_Service
(
    cid  INT,
    sLid INT,
    PRIMARY KEY (cid, sLid),
    FOREIGN KEY (cid) REFERENCES user (cid),
    FOREIGN KEY (sLid) REFERENCES ServiceLocation (sLid)
);
CREATE TABLE Model
(
    modelid    INT PRIMARY KEY AUTO_INCREMENT,
    modeltype  VARCHAR(50) NOT NULL,
    modelname  VARCHAR(50) NOT NULL,
    properties VARCHAR(200)
);

CREATE TABLE Device
(
    deviceid INT PRIMARY KEY AUTO_INCREMENT,
    type     VARCHAR(100) NOT NULL,
    modelid  INT,
    SLid     INT,
    FOREIGN KEY (modelid) REFERENCES Model (modelid),
    FOREIGN KEY (sLid) REFERENCES ServiceLocation (sLid)
);

CREATE TABLE Datas
(
    dataid     INT PRIMARY KEY AUTO_INCREMENT,
    deviceid   INT,
    timestamp  DATETIME    NOT NULL,
    eventLabel VARCHAR(20) NOT NULL,
    value      FLOAT,
    FOREIGN KEY (deviceid) REFERENCES Device (deviceid)
);

CREATE TABLE Price
(
    fromtime TIME  NOT NULL,
    endtime  TIME  NOT NULL,
    zipcode  INT   NOT NULL,
    price    FLOAT NOT NULL,
    PRIMARY KEY (fromtime, endtime, zipcode)
);
