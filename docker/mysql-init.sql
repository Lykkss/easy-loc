CREATE TABLE IF NOT EXISTS Contract (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_uid VARCHAR(255),
    customer_uid VARCHAR(255),
    sign_datetime DATETIME,
    loc_begin_datetime DATETIME,
    loc_end_datetime DATETIME,
    returning_datetime DATETIME,
    price DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS Billing (
    id INT PRIMARY KEY AUTO_INCREMENT,
    contract_id INT,
    amount DECIMAL(10,2),
    FOREIGN KEY (contract_id) REFERENCES Contract(id)
);
