(defunc tail_recursion_loop (i) (
    (var char 0)
    (set char (+ i 48))
    (printc char)
    (print_string "\\n")
    (set i (- i 1))
    (if (= i 0) (0)(funcall tail_recursion_loop (i)))
 ))
(funcall tail_recursion_loop (9))