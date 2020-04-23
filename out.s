main:
li $v0, 9
la $a0, 8
syscall
move arr, $v0
addi !x0, $zero, 0
addi a, !x0, 1
addi !x0, $zero, 0
addi b, !x0, 1
sw a, 0(arr)
sw b, 4(arr)
addi $sp, $sp, -4
sw arr, 0($sp)
addi $sp, $sp, -4
addi !x0, $zero, 2
sw !x0, 0($sp)
addi $sp, $sp, -4
jal arrSum
lw r, 0($sp)
addi $sp, $sp, 12
li $v0, 10
syscall
arrSum:
addi $sp, $sp, -32
sw $s0, 0($sp)
sw $s1, 4($sp)
sw $s2, 8($sp)
sw $s3, 12($sp)
sw $s4, 16($sp)
sw $s5, 20($sp)
sw $s6, 24($sp)
sw $s7, 28($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
addi $sp, $sp, -4
sw $ra, 0($sp)
lw arr, 48($sp)
lw x, 44($sp)
lw a, 0(arr)
lw b, 4(arr)
add c, a, b
add c, c, x
addi $sp, $sp, -4
sw c, 0($sp)
addi $sp, $sp, -4
jal double
lw c, 0($sp)
addi $sp, $sp, 8
lw $ra, 0($sp)
addi $sp, $sp, 4
lw $fp, 0($sp)
addi $sp, $sp, 4
addi $sp, $sp, 32
lw $s7, 0($sp)
lw $s6, -4($sp)
lw $s5, -8($sp)
lw $s4, -12($sp)
lw $s3, -16($sp)
lw $s2, -20($sp)
lw $s1, -24($sp)
lw $s0, -28($sp)
sw c, 0($sp)
jr $ra
double:
addi $sp, $sp, -32
sw $s0, 0($sp)
sw $s1, 4($sp)
sw $s2, 8($sp)
sw $s3, 12($sp)
sw $s4, 16($sp)
sw $s5, 20($sp)
sw $s6, 24($sp)
sw $s7, 28($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
addi $sp, $sp, -4
sw $ra, 0($sp)
lw x, 44($sp)
addi !x0, $zero, 2
mult c, x, !x0
lw $ra, 0($sp)
addi $sp, $sp, 4
lw $fp, 0($sp)
addi $sp, $sp, 4
addi $sp, $sp, 32
lw $s7, 0($sp)
lw $s6, -4($sp)
lw $s5, -8($sp)
lw $s4, -12($sp)
lw $s3, -16($sp)
lw $s2, -20($sp)
lw $s1, -24($sp)
lw $s0, -28($sp)
sw c, 0($sp)
jr $ra
