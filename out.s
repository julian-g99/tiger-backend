main:
li $v0, 5
syscall
move $t0, $v0
loop:
addi $s0, $zero, 0
beq $t0, $s0, end
li $v0, 12
syscall
move $t1, $v0
li $v0, 11
move $a0, $t1
syscall
addi $s0, $zero, 1
sub $t0, $t0, $s0
j loop
end:
li $v0, 1
la $a0, 1
syscall
li $v0, 11
la $a0, 65
syscall
li $v0, 10
syscall
