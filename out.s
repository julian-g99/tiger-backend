fib:
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
addi $sp, $sp, -4
move $fp, $sp
addi $sp, $sp, -36
lw $t1, 48($fp)
addi $t4, $zero, 0
move $t0, $t4
addi $t4, $zero, 1
move $t5, $t4
sw $t0, 0($fp)
lw $t0, -28($fp)
move $t0, $t5
sw $t0, -28($fp)
lw $t0, 0($fp)
addi $t4, $zero, 1
sub $t4, $t1, $t4
bgtz $t4, if_label0
addi $t4, $zero, 0
sw $t0, 0($fp)
lw $t0, -32($fp)
move $t0, $t4
sw $t0, -32($fp)
lw $t0, 0($fp)
move $t5, $t1
sw $t0, 0($fp)
lw $t0, -28($fp)
move $t0, $t5
sw $t0, -28($fp)
lw $t0, 0($fp)
j end
if_label0:
addi $t4, $zero, 1
sub $t1, $t1, $t4
addi $sp, $sp, -40
sw $t0, 0($sp)
sw $t1, 4($sp)
sw $t2, 8($sp)
sw $t3, 12($sp)
sw $t4, 16($sp)
sw $t5, 20($sp)
sw $t6, 24($sp)
sw $t7, 28($sp)
sw $t8, 32($sp)
sw $t9, 36($sp)
addi $sp, $sp, -4
sw $t1, 0($sp)
addi $sp, $sp, -4
jal fib
lw $v0, 0($sp)
addi $sp, $sp, 8
lw $t0, 0($sp)
lw $t1, 4($sp)
lw $t2, 8($sp)
lw $t3, 12($sp)
lw $t4, 16($sp)
lw $t5, 20($sp)
lw $t6, 24($sp)
lw $t7, 28($sp)
lw $t8, 32($sp)
lw $t9, 36($sp)
addi $sp, $sp, 40
move $t2, $v0
addi $t4, $zero, 1
sub $t3, $t1, $t4
addi $t4, $zero, 1
sub $t1, $t1, $t4
addi $sp, $sp, -40
sw $t0, 0($sp)
sw $t1, 4($sp)
sw $t2, 8($sp)
sw $t3, 12($sp)
sw $t4, 16($sp)
sw $t5, 20($sp)
sw $t6, 24($sp)
sw $t7, 28($sp)
sw $t8, 32($sp)
sw $t9, 36($sp)
addi $sp, $sp, -4
sw $t3, 0($sp)
addi $sp, $sp, -4
jal fib
lw $v0, 0($sp)
addi $sp, $sp, 8
lw $t0, 0($sp)
lw $t1, 4($sp)
lw $t2, 8($sp)
lw $t3, 12($sp)
lw $t4, 16($sp)
lw $t5, 20($sp)
lw $t6, 24($sp)
lw $t7, 28($sp)
lw $t8, 32($sp)
lw $t9, 36($sp)
addi $sp, $sp, 40
move $t6, $v0
sw $t1, -4($fp)
lw $t1, -32($fp)
move $t1, $t0
sw $t1, -32($fp)
lw $t1, -4($fp)
move $t5, $t0
add $t5, $t2, $t6
sw $t0, 0($fp)
lw $t0, -28($fp)
move $t0, $t5
sw $t0, -28($fp)
lw $t0, 0($fp)
end:
sw $t0, 0($fp)
lw $t0, -28($fp)
sw $t0, 40($fp)
sw $t0, -28($fp)
lw $t0, 0($fp)
addi $sp, $sp, 36
addi $sp, $sp, 4
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
jr $ra
main:
move $fp, $sp
addi $sp, $sp, -12
addi $sp, $sp, -40
sw $t0, 0($sp)
sw $t1, 4($sp)
sw $t2, 8($sp)
sw $t3, 12($sp)
sw $t4, 16($sp)
sw $t5, 20($sp)
sw $t6, 24($sp)
sw $t7, 28($sp)
sw $t8, 32($sp)
sw $t9, 36($sp)
addi $sp, $sp, -4
addi $t1, $zero, 1
sw $t1, 0($sp)
addi $sp, $sp, -4
jal fib
lw $v0, 0($sp)
addi $sp, $sp, 8
lw $t0, 0($sp)
lw $t1, 4($sp)
lw $t2, 8($sp)
lw $t3, 12($sp)
lw $t4, 16($sp)
lw $t5, 20($sp)
lw $t6, 24($sp)
lw $t7, 28($sp)
lw $t8, 32($sp)
lw $t9, 36($sp)
addi $sp, $sp, 40
move $t2, $v0
move $t0, $t2
li $v0, 1
move $a0, $t0
syscall
li $v0, 11
la $a0, 10
syscall
addi $sp, $sp, 12
li $v0, 10
syscall
