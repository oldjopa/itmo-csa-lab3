(var a 1)
(var b 10)
(defunc fnc (a b c) (
    (set a (10))
    (a)
  ))
(set a (funcall fnc ((+ 10 20) a b)))