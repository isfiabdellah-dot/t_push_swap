/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main_U.c                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nguerrab <nguerrab@student.1337.ma>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/20 18:44:35 by nguerrab          #+#    #+#             */
/*   Updated: 2026/11/28 18:34:37 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

int	ft_memcmp(void *s1, void *s2, int n)
{
	unsigned char	*c1;
	unsigned char	*c2;
	int				i;

	i = 0;
	if (s1 == s2)
		return (0);
	c1 = (unsigned char *)s1;
	c2 = (unsigned char *)s2;
	if (ft_strlen((char *)c1) != ft_strlen((char *)c2))
		return (-1);
	while (i < n)
	{
		if (c1[i] != c2[i])
			return (-1);
		i++;
	}
	return (0);
}

int	isallnum(char *av)
{
	int	i;

	i = 0;
	while (av[i])
	{
		if ((av[i] < '0' || av[i] > '9') && av[i] != ' ')
		{
			if (av[i] != '+' && av[i] != '-')
				return (0);
		}
		i++;
	}
	return (1);
}

int	isnum(char *av)
{
	int	i;

	i = 0;
	while (av[i])
	{
		if (av[i] >= '0' && av[i] <= '9')
			return (1);
		i++;
	}
	return (0);
}

int	ft_strlen(const char *str)
{
	int	i;

	i = 0;
	while (str[i])
		i++;
	return (i);
}

void	error(void)
{
	write(2, "Error\n", 6);
	exit(1);
}
