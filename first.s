fib:
		li t0, 0
		li r, 1
		move rr, r
		li fpt0, 1
		bgt n, fpt0, fib_if_label0
		li t00, 0
		move r, n
		move rr, r
		j fib_end
	fib_if_label0:
		addi n, n, -1
		save_arg $a0
		move $a0, n
		jal fib
		move t1, $v0
		restore_arg $a0
		addi x, n, -1
		addi n, n, -1
		save_arg $a0
		move $a0, x
		jal fib
		move t2, $v0
		restore_arg $a0
		move t00, t0
		move r, t0
		add r, t1, t2
		move rr, r
	fib_end:
		move $v0, rr
		ret
main:
		li $v0, 5
		syscall
		move x, $v0
		save_arg $a0
		move $a0, x
		jal fib
		move z, $v0
		restore_arg $a0
		move x, z
		save_arg $a0
		move $a0, x
		li $v0, 1
		syscall
		restore_arg $a0
		save_arg $a0
		li $a0, 10
		li $v0, 11
		syscall
		restore_arg $a0
