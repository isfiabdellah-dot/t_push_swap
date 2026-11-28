/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nguerrab <nguerrab@student.1337.ma>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/24 15:31:12 by nguerrab          #+#    #+#             */
/*   Updated: 2026/11/28 16:28:27 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "header/push_swap.h"

void	push_swap(t_ctr *s, int flag, float disorder)
{
	if (stack_is_sorted(s->a))
		return ;
	if (flag == 0 || flag == 4)
	{
		if (disorder < 0.2)
			select_sort(s);
		else if (disorder >= 0.2 && disorder < 0.5)
			chunk_sort(s);
		else
			radix_sort(s);
	}
	else
	{
		if (flag == 1)
			select_sort(s);
		else if (flag == 2)
			chunk_sort(s);
		else
			radix_sort(s);
	}
}
