#if !LQT_FUNCTIONS
#define LQT_FUNCTIONS

[@inline]
let maybe (n : nat) : nat option =
  if n = 0n
  then (None : nat option)
  else Some n

#endif