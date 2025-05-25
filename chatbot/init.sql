
CREATE TABLE IF NOT EXISTS UserCredentials (
  UserId   TEXT    NOT NULL PRIMARY KEY,
  Password TEXT    NOT NULL
);


CREATE TABLE IF NOT EXISTS Accounts (
  AccountNumber TEXT    NOT NULL PRIMARY KEY,
  UserId        TEXT    NOT NULL,
  AccountName   TEXT    NOT NULL,
  Balance       NUMERIC NOT NULL,
  CurrencyCode  TEXT    NOT NULL,
  FOREIGN KEY(UserId) REFERENCES UserCredentials(UserId)
);


CREATE TABLE IF NOT EXISTS Transfers (
  TransactionNumber   TEXT    NOT NULL PRIMARY KEY,
  FromAccountNumber   TEXT    NOT NULL,
  ToAccountNumber     TEXT    NOT NULL,
  TransferDateTime    TEXT    NOT NULL,
  Amount              NUMERIC NOT NULL,
  FromAccountBalance  NUMERIC NOT NULL,
  ToAccountBalance    NUMERIC NOT NULL,
  FOREIGN KEY(FromAccountNumber) REFERENCES Accounts(AccountNumber),
  FOREIGN KEY(ToAccountNumber)   REFERENCES Accounts(AccountNumber)
);

CREATE TABLE IF NOT EXISTS Transactions (
  TransactionNumber    NUMERIC NOT NULL,
  AccountNumber        TEXT    NOT NULL,
  OtherAccountNumber   TEXT    NOT NULL,
  TransactionDateTime  TEXT    NOT NULL,
  TransactionTypeCode  TEXT    NOT NULL,
  Amount               NUMERIC NOT NULL,
  BalanceAfter         NUMERIC NOT NULL,
  CONSTRAINT PK_Transactions 
    PRIMARY KEY (TransactionNumber, AccountNumber),
  FOREIGN KEY(AccountNumber)      REFERENCES Accounts(AccountNumber),
  FOREIGN KEY(OtherAccountNumber) REFERENCES Accounts(AccountNumber)
);


INSERT OR IGNORE INTO UserCredentials (UserId, Password)
VALUES 
  ('test1', 'password1'),
  ('test2', 'password2'),
  ('test3', 'passowrd3');


INSERT OR IGNORE INTO Accounts (AccountNumber, UserId, AccountName, Balance, CurrencyCode)
VALUES 
  ('0000000001', 'thebank', 'Bank Withdraw', 0, 'CAD'),
  ('0000000002', 'thebank', 'Bank Deposit', 0, 'CAD'),
  ('1234567890', 'test1', 'Chequing', 100000, 'CAD'),
  ('2345678901', 'test1', 'Saving',   100000, 'CAD'),
  ('3456789012', 'test1', 'Credit Card', 500, 'CAD'),
  ('4567890123', 'test2', 'Chequing', 100000, 'CAD'),
  ('5678901234', 'test2', 'Saving',   100000, 'CAD'),
  ('6789012345', 'test2', 'Credit Card', 500, 'CAD'),
  ('7890123456', 'test3', 'Chequing', 100000, 'CAD'),
  ('8901234567', 'test3', 'Saving',   100000, 'CAD'),
  ('9012345678', 'test3', 'Credit Card', 500, 'CAD');