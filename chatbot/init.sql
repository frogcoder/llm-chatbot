CREATE TABLE UserCredentials (
  UserId   Text NOT NULL PRIMARY KEY,
  Password Text NOT NULL
);

CREATE TABLE Accounts (
  AccountNumber Text    NOT NULL PRIMARY KEY,
  UserId        Text    NOT NULL,
  AccountName   Text    NOT NULL,
  Balance       NUMERIC NOT NULL
);

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
);

INSERT INTO UserCredentials (UserId, Password)
                     VALUES ('test1', 'password1'),
                            ('test2', 'password2'),
                            ('test3', 'passowrd3');

INSERT INTO Accounts (AccountNumber, UserId, AccountName, Balance)
              VALUES ('1234567890', 'test1', 'Checking', 100000),
                     ('2345678901', 'test1', 'Saving', 100000),
                     ('3456789012', 'test1', 'Credit Card', 500),
                     ('4567890123', 'test2', 'Checking', 100000),
                     ('5678901234', 'test2', 'Saving', 100000),
                     ('6789012345', 'test2', 'Credit Card', 500),                     
                     ('7890123456', 'test3', 'Checking', 100000),
                     ('8901234567', 'test3', 'Saving', 100000),
                     ('9012345678', 'test3', 'Credit Card', 500);
                     
