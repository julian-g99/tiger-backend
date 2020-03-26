main:
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
lw $t0, 0($sp)
addi $t0, $zero, 1
sw $t0, 0($sp)
lw $t0, 4($sp)
addi $t0, $zero, 2
sw $t0, 4($sp)
lw $t0, 8($sp)
lw $t1, 0($sp)
lw $t2, 4($sp)
add $t0, $t1, $t2
sw $t0, 8($sp)
sw $t1, 0($sp)
sw $t2, 4($sp)
lw $t1, 4($sp)
lw $t2, 8($sp)
add $a0, $t1, $t2
sw $t1, 4($sp)
sw $t2, 8($sp)
jal, func
lw $t1, 8($sp)
lw $t2, 4($sp)
add $s0, $t1, $t2
sw $t1, 8($sp)
sw $t2, 4($sp)
addi $s0, $s0, 9
end:
j, end
func:
addi $sp, $sp, -12
lw $t0, 12($sp)
sw $t0, 0($sp)
sw $t0, 12($sp)
lw $t0, 16($sp)
sw $t0, 4($sp)
sw $t0, 16($sp)
lw $t0, 20($sp)
sw $t0, 8($sp)
sw $t0, 20($sp)
lw $t0, 12($sp)
addi $t0, $zero, 5
sw $t0, 12($sp)
lw $t0, 16($sp)
addi $t0, $zero, 7
sw $t0, 16($sp)
lw $t0, 20($sp)
lw $t1, 16($sp)
lw $t2, 12($sp)
add $t0, $t1, $t2
sw $t0, 20($sp)
sw $t1, 16($sp)
sw $t2, 12($sp)
lw $t1, 20($sp)
addi $v0, $t1, 3
sw $t1, 20($sp)
lw $t0, 12($sp)
lw $t0, 0($sp)
sw $t0, 12($sp)
lw $t0, 16($sp)
lw $t0, 4($sp)
sw $t0, 16($sp)
lw $t0, 24($sp)
lw $t0, 8($sp)
sw $t0, 24($sp)
addi $sp, $sp, 12
jr $ra