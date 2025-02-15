using extension edgeql_http;
module default {
    type User {
        required property name -> str;
        required property email -> str {
            constraint exclusive;
        }
        required property password -> str;
        required property created_at -> datetime {
            default := datetime_current();
        }
        property last_login -> datetime;
    }

    type Stock {
        required property symbol -> str {
            constraint exclusive;
        }
        required property name -> str;
        required property current_price -> float64;
        required property updated_at -> datetime {
            default := datetime_current();
        }
        multi link transactions -> Transaction;
    }

    type Transaction {
        required property type -> str {
            constraint one_of('buy', 'sell');
        }
        required property quantity -> int64;
        required property price -> float64;
        required property timestamp -> datetime {
            default := datetime_current();
        }
        required link user -> User;
        required link stock -> Stock;
    }

    type Portfolio {
        required link user -> User;
        required link stock -> Stock;
        required property quantity -> int64;
        required property average_price -> float64;
        required property updated_at -> datetime {
            default := datetime_current();
        }
    }
} 