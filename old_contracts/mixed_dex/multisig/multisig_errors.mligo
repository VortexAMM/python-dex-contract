#if !MULTISIG_ERRORS
#define MULTISIG_ERRORS

[@inline] let error_NOT_AN_ADMIN = 1001n
[@inline] let error_ONLY_ADMIN_CAN_PROPOSE = 1002n
[@inline] let _ONLY_SELF_CAN_CALL = 1003n
[@inline] let error_ONLY_SELF_CAN_CALL = 1004n
[@inline] let error_ADMIN_SET_CANNOT_BE_EMPTY = 1005n
[@inline] let error_THRESHOLD_TOO_HIGH = 1006n
[@inline] let error_THRESHOLD_CAN_NOT_BE_ZERO = 1007n
[@inline] let error_DURATION_CANNOT_BE_ZERO = 1008n
[@inline] let error_ALREADY_VOTED = 1008n
[@inline] let error_ONLY_LISTED_CONTRACTS_CAN_CALL = 1009n
[@inline] let error_ADMIN_SET_MUST_BE_LARGER_THAN_THRESHOLD = 1010n
[@inline] let error_ADMINS_COULD_NOT_BE_OBTAINED = 1011n
[@inline] let error_SIGNATURE_SOURCE_NOT_AUTHORIZED = 1012n

#endif