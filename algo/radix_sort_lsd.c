/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   radix_sort_lsd.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/27 10:13:09 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/27 12:01:23 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

void	radix_sort(t_ctr *s)
{
	int	*rk;
	int	bit;
	int	value;
	int	j;

	rk = ranking(s->a);
	if (!rk)
		return ;
	bit = 0;
	while (bit < s->a->capacity)
	{
		j = 0;
		while (j < s->a->capacity)
		{
			value = ft_index(s->a->arr[s->a->head], rk, s->a);
			if ((value >> bit) & 1)
				ra(s);
			else
				pb(s);
			j++;
		}
		while (s->b->size > 0)
			pa(s);
		if (stack_is_sorted(s->a))
			break ;
		bit++;
	}
	free(rk);
}
