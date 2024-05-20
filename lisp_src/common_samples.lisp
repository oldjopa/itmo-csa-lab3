(var a 9)
(if (> a 10) (print_string "T") (print_string "F"))

(var b 10)
(defunc add(c d) (
  (set c (+ c d))
  (c)
  ))
(if (= (funcall add(a b)) 19) (print_string "T") (print_string "F"))
