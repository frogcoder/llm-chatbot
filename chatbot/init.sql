CREATE TABLE UserCredentials (
  UserId   Text NOT NULL PRIMARY KEY,
  Password Text NOT NULL
);

CREATE TABLE Accounts (
  AccountNumber Text    NOT NULL PRIMARY KEY,
  UserId        Text    NOT NULL,
  AccountName   Text    NOT NULL,
  Balance       NUMERIC NOT NULL,
  CurrencyCode  Text    NOT NULL
);

<<<<<<< HEAD
CREATE TABLE Transfers (
  TransactionNumber Text    NOT NULL PRIMARY KEY,
  FromAccountNumber Text    NOT NULL,
  ToAccountNumber   Text    NOT NULL,
  TransferDateTime  Text    NOT NULL,
  Amount            NUMERIC NOT NULL,
  FromAccountBalance NUMERIC NOT NULL,
  ToAccountBalance   NUMERIC NOT NULL,
  FOREIGN KEY(FromAccountNumber) REFERENCES Accounts(AccountNumber),
  FOREIGN KEY(ToAccountNumber)   REFERENCES Accounts(AccountNumber)
=======
CREATE TABLE Transactions (
  TransactionNumber   NUMERIC NOT NULL,
  AccountNumber       Text    NOT NULL,
  OtherAccountNumber  Text    NOT NULL,
  TransactionDateTime Text    NOT NULL,
  TransactionTypeCode Text    NOT NULL,
  Amount              NUMERIC NOT NULL,
  BalanceAfter        NUMERIC NOT NULL,
  CONSTRAINT PK_Transactions      PRIMARY KEY (TransactionNumber, AccountNumber),
  FOREIGN KEY(AccountNumber)      REFERENCES Accounts(AccountNumber),
  FOREIGN KEY(OtherAccountNumber) REFERENCES Accounts(AccountNumber)
>>>>>>> main
);

INSERT INTO UserCredentials (UserId, Password)
                     VALUES ('test1', 'password1'),
                            ('test2', 'password2'),
                            ('test3', 'passowrd3');

INSERT INTO Accounts (AccountNumber, UserId, AccountName, Balance, CurrencyCode)
              VALUES ('0000000001', 'thebank', 'Bank Withdraw', 0, 'CAD'),
                     ('0000000002', 'thebank', 'Bank Deposit', 0, 'CAD'),
                     ('1234567890', 'test1', 'Chequing', 100000, 'CAD'),
                     ('2345678901', 'test1', 'Saving', 100000, 'CAD'),
                     ('3456789012', 'test1', 'Credit Card', 500, 'CAD'),
                     ('4567890123', 'test2', 'Chequing', 100000, 'CAD'),
                     ('5678901234', 'test2', 'Saving', 100000, 'CAD'),
                     ('6789012345', 'test2', 'Credit Card', 500, 'CAD'),                     
                     ('7890123456', 'test3', 'Chequing', 100000, 'CAD'),
                     ('8901234567', 'test3', 'Saving', 100000, 'CAD'),
                     ('9012345678', 'test3', 'Credit Card', 500, 'CAD');
                     
