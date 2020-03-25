main:
addi $t0, $zero, 1
addi $t1, $zero, 2
add $t2, $t0, $t1
add $a0, $t1, $t2
jal func
end:
j end
func:
addi $sp, -12
sw $t0, 0($sp)
sw $t1, 4($sp)
sw $t2, 8($sp)
addi $t0, $zero, 10
addi $v0, $t0, 11
lw $t0, 0($sp)
lw $t1, 4($sp)
sw $t3, 8($sp)
addi $sp, 12
jr $ra