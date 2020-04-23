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
addi $sp, $sp, -36
move $fp, $sp
lw $t1, 80($sp)
addi $t3, $zero, 0
move $t0, $t3
addi $t3, $zero, 1
move $t6, $t3
move $t7, $t6
addi $t3, $zero, 1
sub $t3, $t1, $t3
bgtz $t3, if_label0
addi $t3, $zero, 0
move $t8, $t3
move $t6, $t1
move $t7, $t6
j end
if_label0:
addi $t3, $zero, 1
sub $t1, $t1, $t3
addi $sp, $sp, -4
sw $t1, 0($sp)
addi $sp, $sp, -4
jal fib
lw $t2, 0($sp)
addi $sp, $sp, 8
addi $t3, $zero, 1
sub $t4, $t1, $t3
addi $t3, $zero, 1
sub $t1, $t1, $t3
addi $sp, $sp, -4
sw $t4, 0($sp)
addi $sp, $sp, -4
jal fib
lw $t5, 0($sp)
addi $sp, $sp, 8
move $t8, $t0
move $t6, $t0
add $t6, $t2, $t5
move $t7, $t6
end:
addi $sp, $sp, 36
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
sw $t7, 0($sp)
jr $ra
main:
addi $sp, $sp, -8
move $fp, $sp
li $v0, 5
syscall
move $t0, $v0
addi $sp, $sp, -4
sw $t0, 0($sp)
addi $sp, $sp, -4
jal fib
lw $t1, 0($sp)
addi $sp, $sp, 8
move $t0, $t1
li $v0, 1
move $a0, $t0
syscall
li $v0, 11
la $a0, 10
syscall
addi $sp, $sp, 8
li $v0, 10
syscall
