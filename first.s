quicksort:
		li i, 0
		li j, 0
		bge lo, hi, quicksort_end
		add mid, lo, hi
		li fpt1, 2
		div mid, mid, fpt1
		move fpt2, mid
		sll fpt2, fpt2, 2
		addu fpt2, A, fpt2
		lw pivot, (fpt2)
		addi i, lo, -1
		addi j, hi, 1
	quicksort_loop0:
	quicksort_loop1:
		addi i, i, 1
		move fpt3, i
		sll fpt3, fpt3, 2
		addu fpt3, A, fpt3
		lw x, (fpt3)
		move ti, x
		blt ti, pivot, quicksort_loop1
	quicksort_loop2:
		addi j, j, -1
		move fpt5, j
		sll fpt5, fpt5, 2
		addu fpt5, A, fpt5
		lw x, (fpt5)
		move tj, x
		bgt tj, pivot, quicksort_loop2
		bge i, j, quicksort_exit0
		move fpt8, j
		sll fpt8, fpt8, 2
		addu fpt8, A, fpt8
		sw ti, (fpt8)
		move fpt9, i
		sll fpt9, fpt9, 2
		addu fpt9, A, fpt9
		sw tj, (fpt9)
		j quicksort_loop0
	quicksort_exit0:
		addi j1, j, 1
		save_arg $a0
		save_arg $a1
		save_arg $a2
		move $a0, A
		move $a1, lo
		move $a2, j
		jal quicksort
		restore_arg $a0
		restore_arg $a1
		restore_arg $a2
		addi j, j, 1
		save_arg $a0
		save_arg $a1
		save_arg $a2
		move $a0, A
		move $a1, j
		move $a2, hi
		jal quicksort
		restore_arg $a0
		restore_arg $a1
		restore_arg $a2
	quicksort_end:
main:
		li t, 0
		li $v0, 5
		syscall
		move n, $v0
		li fpt12, 100
		bgt n, fpt12, main_return
		addi n, n, -1
		li i, 0

	main_loop0:
		bgt i, n, main_exit0

		li $v0, 5
		syscall
		move t, $v0
		move fpt14, i
		sll fpt14, fpt14, 2
		addu fpt14, A, fpt14
		sw t, (fpt14)
		addi i, i, 1
		j main_loop0

	main_exit0:
		save_arg $a0
		save_arg $a1
		save_arg $a2
		move $a0, A
		li $a1, 0
		move $a2, n
		jal quicksort
		restore_arg $a0
		restore_arg $a1
		restore_arg $a2
		li i, 0
	main_loop1:
		bgt i, n, main_exit1
		move fpt17, i
		sll fpt17, fpt17, 2
		addu fpt17, A, fpt17
		lw t, (fpt17)
		save_arg $a0
		move $a0, t
		li $v0, 1
		syscall
		restore_arg $a0
		save_arg $a0
		li $a0, 10
		li $v0, 11
		syscall
		restore_arg $a0
		addi i, i, 1
		j main_loop1
	main_exit1:
	main_return:
quicksort
{'$a0': -4,
 '$a1': -8,
 '$a2': -12,
 '$a3': -16,
 '$ra': -116,
 '$t0': -76,
 '$t1': -80,
 '$t2': -84,
 '$t3': -88,
 '$t4': -92,
 '$t5': -96,
 '$t6': -100,
 '$t7': -104,
 '$t8': -108,
 '$t9': -112,
 'fpt1': -20,
 'fpt2': -24,
 'fpt3': -28,
 'fpt5': -32,
 'fpt8': -36,
 'fpt9': -40,
 'i': -44,
 'j': -48,
 'j1': -52,
 'mid': -56,
 'pivot': -60,
 'ti': -64,
 'tj': -68,
 'x': -72}
{'A': '$a0', 'hi': '$a2', 'i': '$t1', 'j': '$t0', 'lo': '$a1'}
{'A': '$a0',
 'fpt1': '$t2',
 'fpt2': '$t0',
 'hi': '$a2',
 'i': '$t5',
 'j': '$t4',
 'lo': '$a1',
 'mid': '$t1',
 'pivot': '$t3'}
{'A': '$a0', 'hi': '$a2', 'lo': '$a1'}
{'A': '$a0',
 'fpt3': '$t0',
 'hi': '$a2',
 'i': '$t3',
 'lo': '$a1',
 'pivot': '$t4',
 'ti': '$t2',
 'x': '$t1'}
{'A': '$a0',
 'fpt5': '$t0',
 'hi': '$a2',
 'j': '$t3',
 'lo': '$a1',
 'pivot': '$t4',
 'tj': '$t1',
 'x': '$t2'}
{'A': '$a0', 'hi': '$a2', 'i': '$t1', 'j': '$t0', 'lo': '$a1'}
{'A': '$a0',
 'fpt8': '$t1',
 'fpt9': '$t0',
 'hi': '$a2',
 'i': '$t5',
 'j': '$t4',
 'lo': '$a1',
 'ti': '$t3',
 'tj': '$t2'}
{'A': '$a0', 'hi': '$a2', 'j': '$t0', 'j1': '$t1', 'lo': '$a1'}
{'A': '$a0', 'hi': '$a2', 'lo': '$a1'}
{'fpt12': '$t1', 'n': '$t0', 't': '$t2'}
{'i': '$t1', 'n': '$t0'}
{'i': '$t1', 'n': '$t0'}
{'A': '$t3', 'fpt14': '$t0', 'i': '$t2', 't': '$t1'}
{'A': '$t0', 'i': '$t2', 'n': '$t1'}
{'i': '$t1', 'n': '$t0'}
{'A': '$t3', 'fpt17': '$t0', 'i': '$t2', 't': '$t1'}
{}
{}
