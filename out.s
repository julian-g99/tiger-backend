pow:
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
addi $sp, $sp, -24
lw $t0, 52($fp)
lw $t1, 48($fp)
sw $t0, -4($fp)
lw $t0, -12($fp)
addi $t0, $zero, 0
sw $t0, -12($fp)
lw $t0, -4($fp)
sw $t0, -4($fp)
lw $t0, -12($fp)
bne $t1, $t0, LABEL0
sw $t0, -12($fp)
lw $t0, -4($fp)
sw $t0, -4($fp)
lw $t0, -12($fp)
addi $t0, $zero, 1
sw $t0, -12($fp)
lw $t0, -4($fp)
sw $t0, -4($fp)
lw $t0, -12($fp)
sw $t1, -8($fp)
lw $t1, -16($fp)
move $t1, $t0
sw $t0, -12($fp)
lw $t0, -4($fp)
sw $t1, -16($fp)
lw $t1, -8($fp)
j RET
LABEL0:
sw $t0, -4($fp)
lw $t0, -12($fp)
addi $t0, $zero, 2
sw $t0, -12($fp)
lw $t0, -4($fp)
sw $t0, -4($fp)
lw $t0, -12($fp)
div $t1, $t0
sw $t0, -12($fp)
lw $t0, -4($fp)
mflo $t2
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
sw $t0, 0($sp)
addi $sp, $sp, -4
sw $t2, 0($sp)
addi $sp, $sp, -4
jal pow
lw $v0, 0($sp)
addi $sp, $sp, 12
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
move $t3, $v0
mult $t3, $t3
mflo $t3
sw $t0, -4($fp)
lw $t0, -16($fp)
move $t0, $t3
sw $t0, -16($fp)
lw $t0, -4($fp)
sw $t0, -4($fp)
lw $t0, -12($fp)
addi $t0, $zero, 2
sw $t0, -12($fp)
lw $t0, -4($fp)
sw $t0, -4($fp)
lw $t0, -12($fp)
mult $t2, $t0
sw $t0, -12($fp)
lw $t0, -4($fp)
mflo $t2
beq $t2, $t1, RET
mult $t3, $t0
mflo $t3
sw $t0, -4($fp)
lw $t0, -16($fp)
move $t0, $t3
sw $t0, -16($fp)
lw $t0, -4($fp)
RET:
sw $t0, -4($fp)
lw $t0, -16($fp)
sw $t0, 44($fp)
sw $t0, -16($fp)
lw $t0, -4($fp)
addi $sp, $sp, 24
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
addi $sp, $sp, -16
addi $t2, $zero, 8
move $t0, $t2
addi $t2, $zero, 1
move $t1, $t2
addi $t2, $zero, 0
sub $t2, $t1, $t2
bltz $t2, END
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
sw $t0, 0($sp)
addi $sp, $sp, -4
sw $t1, 0($sp)
addi $sp, $sp, -4
jal pow
lw $v0, 0($sp)
addi $sp, $sp, 12
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
move $t3, $v0
li $v0, 1
move $a0, $t3
syscall
li $v0, 11
la $a0, 10
syscall
END:
addi $sp, $sp, 16
li $v0, 10
syscall
