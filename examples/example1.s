main:
addi $t1, $zero, 1
addi $t0, $zero, 2
addi $t2, $zero, 4
add $t3, $t1, $t0
sub $t0, $t3, $t1
addi $t3, $t2, 3
add $t1, $t1, $t1
add $t3, $t0, $t1
add $t2, $t0, $t3
add $a0, $zero, $t2
end:
j, end