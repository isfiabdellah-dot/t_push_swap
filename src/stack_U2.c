/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_U2.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nguerrab <nguerrab@student.1337.ma>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/23 19:49:25 by nguerrab          #+#    #+#             */
/*   Updated: 2026/11/28 17:35:44 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

void	stack_swap(t_stack *s)//valid
{
	int	tmp;

	if (s->size >= 2)
	{
		tmp = s->arr[s->head];
		s->arr[s->head] = s->arr[(s->head + 1) % s->capacity];
		s->arr[(s->head + 1) % s->capacity] = tmp;
	}
}

void	stack_free(t_stack *s)//valid
{
	if (!s)
		return ;
	free(s->arr);
	free(s);
}

int	stack_pop(t_stack *s, int *val)//valid; return = val or ERROR
{
	if (s->size == 0)
		return (0);
	*val = s->arr[s->head];
	s->head = (s->head + 1) % s->capacity;
	s->size--;
	return (1);
}

void	rrr(t_ctr *s)//valide
{
	int	a;
	int	b;

	a = stack_shift_down(s->a);
	b = stack_shift_down(s->b);
	if (!a && !b)
		return ;
	s->rrr++;
	write(1, "rrr\n", 4);
}

void	stack_push(int val, t_stack *s)//3amrha fial
{
	if (s->size < s->capacity)
	{
		s->head = (s->head - 1 + s->capacity) % s->capacity;
		s->arr[s->head] = val;
		s->size++;
	}
}
